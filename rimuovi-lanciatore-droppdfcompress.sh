#!/usr/bin/env bash
    set -u

    APP_NAME="DropPDFCompress"
    APP_ID="droppdfcompress"

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
    DESKTOP_SRC="$SCRIPT_DIR/DropPDFCompress.desktop"

    LOCAL_BIN_DIR="$HOME/.local/bin"
    LOCAL_APP_DIR="$HOME/.local/share/applications"
    LOCAL_ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"

    LAUNCHER_PATH="$LOCAL_BIN_DIR/$APP_ID"
    DESKTOP_PATH="$LOCAL_APP_DIR/$APP_ID.desktop"
    ICON_DEST="$LOCAL_ICON_DIR/$APP_ID.svg"

    log() {
      printf '%s\n' "$*"
    }

    warn() {
      printf 'Attenzione: %s\n' "$*" >&2
    }

    remove_if_exists() {
      local target="$1"
      if [ -e "$target" ] || [ -L "$target" ]; then
        rm -f "$target" && log "Rimosso: $target" || warn "Impossibile rimuovere: $target"
      else
        log "Non presente: $target"
      fi
    }

    log "Disinstallazione di $APP_NAME in corso..."
    log ""

    remove_if_exists "$LAUNCHER_PATH"
    remove_if_exists "$DESKTOP_PATH"
    remove_if_exists "$ICON_DEST"

    if [ -f "$DESKTOP_SRC" ]; then
      log "File del progetto lasciato invariato: $DESKTOP_SRC"
    fi

    rmdir "$LOCAL_ICON_DIR" 2>/dev/null || true
    rmdir "$HOME/.local/share/icons/hicolor/scalable" 2>/dev/null || true
    rmdir "$HOME/.local/share/icons/hicolor" 2>/dev/null || true
    rmdir "$HOME/.local/share/icons" 2>/dev/null || true
    rmdir "$LOCAL_APP_DIR" 2>/dev/null || true
    rmdir "$LOCAL_BIN_DIR" 2>/dev/null || true

    if command -v update-desktop-database >/dev/null 2>&1; then
      update-desktop-database "$HOME/.local/share/applications" >/dev/null 2>&1 || true
    fi

    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
      gtk-update-icon-cache "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
    fi

    if command -v xdg-desktop-menu >/dev/null 2>&1; then
      xdg-desktop-menu forceupdate >/dev/null 2>&1 || true
    fi

    log ""
    log "Disinstallazione completata."
    log "Se il launcher o l'icona restano visibili nel menu, esci e rientra nella sessione oppure riavvia il pannello/menu."
