#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nome programma: DropPDFCompress v.2026-05
Autore: Gianluca Bolognesi
Versione: Maggio 2026
Descrizione: Utilità drag & drop per Linux che trasforma file in PDF e permette
             di comprimere il PDF scegliendo il livello di compressione.

Dipendenze consigliate:
  sudo apt install python3-pyqt6 libreoffice ghostscript qpdf poppler-utils

Avvio:
  python3 DropPDFCompress.py
"""

import os
import sys
import time
import shutil
import tempfile
import subprocess
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPixmap, QPainter
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QProgressBar,
    QStatusBar,
    QSystemTrayIcon,
    QVBoxLayout,
    QWidget,
)


class CompressionPreset:
    def __init__(self, name, dpi, quality, ratio, description=""):
        self.name = name
        self.label = name
        self.dpi = dpi
        self.quality = quality
        self.ratio = ratio
        self.estimated_ratio = ratio
        self.description = description

PRESETS = {
    "Buono / leggibile 150 dpi": CompressionPreset(
        "Buono / leggibile 150 dpi", 150, 0.65, 0.70,
        "Qualità alta, riduzione moderata. Utile per documenti da conservare."
    ),
    "Medio 120 dpi": CompressionPreset(
        "Medio 120 dpi", 120, 0.55, 0.50,
        "Default consigliato: buon equilibrio tra qualità e dimensione."
    ),
    "Forte 96 dpi": CompressionPreset(
        "Forte 96 dpi", 96, 0.45, 0.35,
        "Compressione decisa. Buona per invii via email o archiviazione leggera."
    ),
    "Estremo 72 dpi": CompressionPreset(
        "Estremo 72 dpi", 72, 0.35, 0.22,
        "Massima riduzione, possibile perdita visibile di qualità."
    ),
}


class CompressionDialog(QDialog):
    def __init__(self, parent, source_name, source_size, pdf_size=None):
        super().__init__(parent)
        self.setWindowTitle("Scegli compressione PDF")
        self.setMinimumWidth(520)
        self.source_name = source_name
        self.source_size = source_size
        self.pdf_size = pdf_size or source_size

        layout = QVBoxLayout(self)

        title = QLabel(f"File: {source_name}")
        title.setFont(QFont("sans-serif", 13, QFont.Weight.Bold))
        layout.addWidget(title)

        self.info_label = QLabel()
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        grid = QGridLayout()
        grid.addWidget(QLabel("Compressione:"), 0, 0)
        self.combo = QComboBox()
        self.combo.addItems(PRESETS.keys())
        self.combo.setCurrentText("Medio 120 dpi")
        grid.addWidget(self.combo, 0, 1)
        layout.addLayout(grid)

        self.estimate_label = QLabel()
        self.estimate_label.setStyleSheet("font-size: 12pt; padding: 8px;")
        self.estimate_label.setWordWrap(True)
        layout.addWidget(self.estimate_label)

        self.combo.currentTextChanged.connect(self.update_estimate)
        self.update_estimate()

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("OK comprimi")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Annulla")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def human_size(num):
        value = float(num)
        for unit in ["B", "KB", "MB", "GB"]:
            if value < 1024 or unit == "GB":
                return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
            value /= 1024
        return f"{value:.1f} GB"

    def update_estimate(self):
        preset = PRESETS[self.combo.currentText()]
        estimated = max(1, int(self.pdf_size * preset.estimated_ratio))
        self.info_label.setText(
            f"Dimensione originale: {self.human_size(self.source_size)}\n"
            f"Dimensione PDF di partenza: {self.human_size(self.pdf_size)}"
        )
        self.estimate_label.setText(
            f"Stima finale ipotetica: circa {self.human_size(estimated)}\n"
            f"Preset: {preset.description}\n"
            "Nota: la stima è indicativa; il risultato reale dipende da immagini, font e struttura del PDF."
        )

    def selected_preset(self):
        return PRESETS[self.combo.currentText()]


class DropPDFCompress(QWidget):
    def __init__(self):
        super().__init__()
        self.base_dir = Path(__file__).resolve().parent
        self.local_tmp_dir = self.base_dir / "tmp_droppdfcompress"
        self.local_tmp_dir.mkdir(exist_ok=True)
        self.init_ui()
        self.init_tray()

    def init_ui(self):
        self.setWindowTitle("DropPDFCompress")
        self.setMinimumSize(820, 580)
        self.setWindowIcon(self.build_app_icon())

        main_layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        header = QLabel("DropPDFCompress")
        header.setFont(QFont("sans-serif", 22, QFont.Weight.Bold))
        top_layout.addWidget(header)
        top_layout.addStretch()
        author = QLabel("Autore: Gianluca Bolognesi")
        author.setFont(QFont("sans-serif", 10))
        top_layout.addWidget(author)
        main_layout.addLayout(top_layout)

        self.drop_frame = QFrame()
        self.drop_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        self.drop_frame.setStyleSheet(
            "QFrame { border: 3px dashed #d32f2f; border-radius: 20px; background-color: #fff5f5; }"
        )

        frame_layout = QVBoxLayout(self.drop_frame)
        self.drop_label = QLabel(
            "Trascina qui un file da trasformare in PDF e comprimere\n"
            "Supporta PDF, immagini, TXT/LOG e documenti LibreOffice/Office"
        )
        self.drop_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_label.setFont(QFont("sans-serif", 12))
        frame_layout.addWidget(self.drop_label)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        frame_layout.addWidget(self.progress)

        self.file_list = QListWidget()
        self.file_list.setStyleSheet(
            "QListWidget { background: white; border-radius: 10px; padding: 5px; font-size: 12pt; }"
        )
        frame_layout.addWidget(self.file_list)
        main_layout.addWidget(self.drop_frame)

        self.status_bar = QStatusBar()
        main_layout.addWidget(self.status_bar)
        self.setLayout(main_layout)
        self.setAcceptDrops(True)

    def build_app_icon(self):
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#d32f2f"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(4, 4, 56, 56, 12, 12)
        painter.setPen(QColor("white"))
        painter.setFont(QFont("sans-serif", 22, QFont.Weight.Bold))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "PDF")
        painter.end()
        return QIcon(pixmap)

    def init_tray(self):
        self.tray_icon = None
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.windowIcon())
        self.tray_icon.setToolTip("DropPDFCompress")

        tray_menu = QMenu()
        show_action = QAction("Apri DropPDFCompress", self)
        show_action.triggered.connect(self.show_normal)
        tray_menu.addAction(show_action)

        hide_action = QAction("Nascondi", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()

        info_action = QAction("Info", self)
        info_action.triggered.connect(self.show_about)
        tray_menu.addAction(info_action)
        tray_menu.addSeparator()

        quit_action = QAction("Esci", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_normal() if not self.isVisible() else self.hide()

    def show_normal(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def show_about(self):
        QMessageBox.information(
            self,
            "Informazioni su DropPDFCompress",
            "DropPDFCompress\n\n"
            "Autore: Gianluca Bolognesi\n"
            "Versione: 2026-05\n"
            "Funzione: conversione e compressione PDF drag & drop"
        )

    def closeEvent(self, event):
        if self.tray_icon and self.tray_icon.isVisible():
            self.hide()
            self.tray_icon.showMessage(
                "DropPDFCompress",
                "L'applicazione resta attiva nel vassoio di sistema.",
                QSystemTrayIcon.MessageIcon.Information,
                2500,
            )
            event.ignore()
            return
        event.accept()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
            self.drop_frame.setStyleSheet(
                "QFrame { border: 3px solid #b71c1c; background-color: #ffebee; border-radius: 20px; }"
            )
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        self.reset_drop_style()

    def dropEvent(self, event):
        self.reset_drop_style()
        files = [u.toLocalFile() for u in event.mimeData().urls() if u.isLocalFile()]
        for file_path in files:
            self.process_file(file_path)

    def reset_drop_style(self):
        self.drop_frame.setStyleSheet(
            "QFrame { border: 3px dashed #d32f2f; border-radius: 20px; background-color: #fff5f5; }"
        )

    @staticmethod
    def command_exists(name):
        return shutil.which(name) is not None

    def ensure_dependencies(self):
        missing = []
        if not (self.command_exists("libreoffice") or self.command_exists("soffice")):
            missing.append("libreoffice")
        if not self.command_exists("gs"):
            missing.append("ghostscript")
        if missing:
            QMessageBox.critical(
                self,
                "Dipendenze mancanti",
                "Mancano questi programmi:\n\n"
                + "\n".join(f"- {m}" for m in missing)
                + "\n\nInstalla ad esempio con:\n"
                "sudo apt install libreoffice ghostscript qpdf poppler-utils"
            )
            return False
        return True

    def convert_to_pdf(self, input_file):
        input_path = Path(input_file)
        ext = input_path.suffix.lower()

        if ext == ".pdf":
            return str(input_path), None, False

        job_tmp_dir = self.local_tmp_dir / f"{input_path.stem}_{int(time.time())}"
        job_tmp_dir.mkdir(parents=True, exist_ok=True)

        image_exts = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".gif"}
        text_exts = {".txt", ".log", ".csv"}
        office_exts = {
            ".odt", ".ods", ".odp", ".doc", ".docx", ".xls", ".xlsx",
            ".ppt", ".pptx", ".rtf", ".html", ".htm"
        }

        # LibreOffice gestisce bene documenti Office/LibreOffice e testi.
        if ext in office_exts or ext in text_exts or ext in image_exts:
            libreoffice_cmd = shutil.which("libreoffice") or shutil.which("soffice")
            if not libreoffice_cmd:
                return None, None, False

            lo_profile_dir = Path(tempfile.gettempdir()) / "droppdfcompress-lo-profile"
            lo_profile_dir.mkdir(parents=True, exist_ok=True)

            self.status_bar.showMessage(f"Conversione in PDF: {input_path.name}", 5000)
            QApplication.processEvents()

            result = subprocess.run(
                [
                    libreoffice_cmd,
                    "--headless",
                    "--nologo",
                    "--nolockcheck",
                    "--nodefault",
                    "--norestore",
                    f"-env:UserInstallation=file://{lo_profile_dir}",
                    "--convert-to", "pdf:writer_pdf_Export",
                    "--outdir", str(job_tmp_dir),
                    str(input_path),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )

            expected = job_tmp_dir / f"{input_path.stem}.pdf"
            if expected.exists():
                return str(expected), str(job_tmp_dir), True

            # Alcuni filtri LibreOffice possono cambiare leggermente nome: prendo il primo PDF creato.
            pdfs = list(job_tmp_dir.glob("*.pdf"))
            if pdfs:
                return str(pdfs[0]), str(job_tmp_dir), True

            print("LibreOffice stdout:", result.stdout)
            print("LibreOffice stderr:", result.stderr)
            return None, str(job_tmp_dir), True

        return None, None, False

    def output_path_for(self, original_file):
        original = Path(original_file)
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
        return original.with_name(f"{original.stem}_compressed_{timestamp}.pdf")

    def compress_pdf(self, input_pdf, output_pdf, preset: CompressionPreset):
        tmp_pdf = str(Path(output_pdf).with_suffix(".tmp.pdf"))
        jpeg_quality = int(preset.quality * 100)

        gs_cmd = [
            "gs", "-q", "-dNOPAUSE", "-dBATCH", "-dSAFER",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.5",
            "-dPDFSETTINGS=/screen",
            "-dDetectDuplicateImages=true",
            "-dCompressFonts=true",
            "-dSubsetFonts=true",
            "-dCompressStreams=true",
            "-dAutoRotatePages=/None",
            "-dDownsampleColorImages=true",
            "-dColorImageDownsampleType=/Bicubic",
            f"-dColorImageResolution={preset.dpi}",
            "-dDownsampleGrayImages=true",
            "-dGrayImageDownsampleType=/Bicubic",
            f"-dGrayImageResolution={preset.dpi}",
            "-dDownsampleMonoImages=true",
            "-dMonoImageDownsampleType=/Subsample",
            f"-dMonoImageResolution={preset.dpi}",
            "-dColorImageFilter=/DCTEncode",
            "-dGrayImageFilter=/DCTEncode",
            f"-dJPEGQ={jpeg_quality}",
            f"-sOutputFile={tmp_pdf}",
            input_pdf,
        ]

        result = subprocess.run(gs_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        if result.returncode != 0 or not Path(tmp_pdf).exists():
            print("Ghostscript stdout:", result.stdout)
            print("Ghostscript stderr:", result.stderr)
            return False

        if self.command_exists("qpdf"):
            qpdf_result = subprocess.run(
                ["qpdf", "--object-streams=generate", "--stream-data=compress", tmp_pdf, output_pdf],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
            try:
                os.remove(tmp_pdf)
            except OSError:
                pass
            if qpdf_result.returncode != 0 or not Path(output_pdf).exists():
                print("qpdf stdout:", qpdf_result.stdout)
                print("qpdf stderr:", qpdf_result.stderr)
                return False
        else:
            shutil.move(tmp_pdf, output_pdf)

        return Path(output_pdf).exists()

    def process_file(self, file_path):
        if not self.ensure_dependencies():
            return

        source = Path(file_path)
        if not source.exists() or not source.is_file():
            QMessageBox.warning(self, "File non valido", f"File non trovato:\n{file_path}")
            return

        item = QListWidgetItem(f"⏳ Preparazione: {source.name}")
        item.setForeground(QColor("darkorange"))
        self.file_list.addItem(item)
        QApplication.processEvents()

        temp_dir = None
        try:
            self.progress.setVisible(True)
            self.progress.setRange(0, 0)

            pdf_file, temp_dir, was_converted = self.convert_to_pdf(str(source))
            if not pdf_file:
                item.setText(f"❌ Conversione fallita: {source.name}")
                item.setForeground(QColor("darkred"))
                QMessageBox.warning(
                    self,
                    "Conversione fallita",
                    f"Non riesco a trasformare questo file in PDF:\n{source.name}\n\n"
                    "Avvia il programma da terminale per vedere eventuali dettagli."
                )
                return

            source_size = source.stat().st_size
            pdf_size = Path(pdf_file).stat().st_size
            dialog = CompressionDialog(self, source.name, source_size, pdf_size)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                item.setText(f"⛔ Annullato: {source.name}")
                item.setForeground(QColor("gray"))
                return

            preset = dialog.selected_preset()
            output_pdf = self.output_path_for(str(source))

            item.setText(f"🗜️ Compressione {preset.label}: {source.name}")
            item.setForeground(QColor("darkorange"))
            self.status_bar.showMessage(f"Compressione in corso: {source.name}", 5000)
            QApplication.processEvents()

            ok = self.compress_pdf(pdf_file, str(output_pdf), preset)
            if not ok:
                item.setText(f"❌ Compressione fallita: {source.name}")
                item.setForeground(QColor("darkred"))
                QMessageBox.critical(self, "Errore", f"Compressione fallita per:\n{source.name}")
                return

            original_h = CompressionDialog.human_size(source_size)
            final_h = CompressionDialog.human_size(output_pdf.stat().st_size)
            item.setText(f"✅ Creato: {output_pdf.name} | Prima: {original_h} | Dopo: {final_h}")
            item.setForeground(QColor("green"))
            self.status_bar.showMessage(f"Creato: {output_pdf}", 7000)

            if self.tray_icon:
                self.tray_icon.showMessage(
                    "DropPDFCompress",
                    f"Creato: {output_pdf.name}\nPrima: {original_h} - Dopo: {final_h}",
                    QSystemTrayIcon.MessageIcon.Information,
                    3500,
                )

        except Exception as exc:
            item.setText(f"❌ Errore: {source.name}")
            item.setForeground(QColor("darkred"))
            QMessageBox.critical(self, "Errore", str(exc))
        finally:
            self.progress.setVisible(False)
            self.progress.setRange(0, 100)
            if temp_dir and Path(temp_dir).exists():
                shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DropPDFCompress")
    app.setQuitOnLastWindowClosed(False)
    app.setStyle("Fusion")

    window = DropPDFCompress()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
