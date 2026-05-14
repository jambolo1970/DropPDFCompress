# DropPDFCompress 📄🔻

DropPDFCompress è una piccola applicazione desktop per Linux, principalmente pensata per **openSUSE** e **Linux Mint**, ma compatibile anche con altre distribuzioni Linux.

Permette di:

- trascinare file direttamente nella finestra
- convertirli automaticamente in PDF
- comprimere i PDF scegliendo il livello di qualità
- stimare la dimensione finale del file
- creare automaticamente un nuovo PDF compresso mantenendo il nome originale

Il tutto tramite una semplice interfaccia drag-and-drop in stile DropPrint.

L'applicazione utilizza:

- LibreOffice per le conversioni
- Ghostscript per la compressione PDF
- PyQt per l'interfaccia grafica

Il file originale NON viene modificato.
Viene creato un nuovo file con data e ora nel nome.

Esempio:

```text
fattura.pdf
fattura_compressed_2026-05-14_16-44-12.pdf
```

---

# ℹ️ Funzioni principali

- drag and drop multiplo
- conversione automatica in PDF
- compressione PDF avanzata
- scelta qualità compressione:
  - Buono / leggibile 150 dpi
  - Medio 120 dpi (default)
  - Forte 96 dpi
  - Estremo 72 dpi
- stima dimensione finale
- mantenimento file originale
- creazione automatica file con timestamp
- supporto LibreOffice / OpenOffice
- interfaccia grafica semplice
- colori stile PDF rosso/bianco
- launcher automatico Linux
- integrazione menu applicazioni

---

# 🚀 Caratteristiche

- 📄 Conversione automatica documenti → PDF
- 🔻 Compressione intelligente PDF
- 🖱️ Drag-and-drop immediato
- 📋 Elaborazione multipla file
- 📁 File originale preservato
- 🐧 Ottimizzato per Linux desktop
- ⚡ Utilizzo semplice e rapido

---

# 📄 Formati supportati

## PDF diretti

- `.pdf` nato principalmente per ridurre il peso del pdf

## File convertibili automaticamente

### LibreOffice / OpenOffice

- `.odt - .ods - .odp`

### Microsoft Office

- `.doc - .docx`
- `.xls - .xlsx`
- `.ppt - .pptx`

### Altri formati

- `.rtf - .csv - .txt`

---

# ⚙️ Requisiti

## Linux

- CUPS opzionale
- Ghostscript
- LibreOffice
- Python 3
- PyQt5 o PyQt6

## Pacchetti richiesti

### openSUSE 🦎

```bash
sudo zypper install ghostscript libreoffice python3 python3-qt6
```

### Linux Mint / Ubuntu

```bash
sudo apt install ghostscript libreoffice python3 python3-pyqt5
```

---

# 🖥️ Installazione

## Metodo ZIP

- Scarica lo ZIP del progetto
- Estrai la cartella
- Apri un terminale dentro la cartella

## Metodo Git

```bash
git clone https://github.com/jambolo1970/droppdfcompress.git
cd droppdfcompress
```

---

# 🚀 Avvio rapido

Rendi eseguibile il programma:

```bash
chmod +x DropPDFCompress.py
```

Avvio:

```bash
python3 DropPDFCompress.py
```

---

# 🖥️ Installazione launcher Linux

Per creare automaticamente:

- icona nel menu
- launcher desktop
- integrazione sistema
- avvio senza terminale

eseguire:

```bash
chmod +x installa-lanciatore-droppdfcompress.sh
./installa-lanciatore-droppdfcompress.sh
```

Dopo l'installazione il programma sarà presente nel menu applicazioni come:

```text
DropPDFCompress
```

---

# ♻️ Disinstallazione launcher

```bash
chmod +x rimuovi-lanciatore-droppdfcompress.sh
./rimuovi-lanciatore-droppdfcompress.sh
```

---

# 👨‍🔧 Note tecniche

- il programma usa Ghostscript per comprimere i PDF
- LibreOffice viene usato in modalità headless
- la compressione avviene senza modificare il file originale
- i file temporanei vengono eliminati automaticamente
- la stima finale è indicativa e dipende dal contenuto del PDF
- PDF con molte immagini ottengono compressioni migliori

---

# 🔻 Livelli compressione

| Livello | DPI | Uso consigliato |
|---|---|---|
| Buono | 150 dpi | archiviazione documenti |
| Medio | 120 dpi | uso generale ✅default|
| Forte | 96 dpi | invio email |
| Estremo | 72 dpi | documenti molto pesanti |

---

# 🐧 Compatibilità Linux

Testato principalmente su:

- openSUSE
- Linux Mint
- Ubuntu
- KDE Plasma
- XFCE
- Cinnamon

---

# 👨‍💻 Autore

Gianluca Bolognesi

---

# 📜 Licenza

GPL 3

