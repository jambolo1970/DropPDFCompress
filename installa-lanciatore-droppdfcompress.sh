\
    #!/usr/bin/env bash
    set -u

    APP_NAME="DropPDFCompress"
    APP_ID="droppdfcompress"
    APP_COMMENT="Converti e comprimi PDF con drag and drop"
    APP_WM_CLASS="DropPDFCompress"

    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

    # Cerca automaticamente il file principale nella stessa cartella.
    CANDIDATES=(
      "DropPDFCompress.py"
      "droppdfcompress.py"
    )

    APP_SCRIPT=""
    for candidate in "${CANDIDATES[@]}"; do
      if [ -f "$SCRIPT_DIR/$candidate" ]; then
        APP_SCRIPT="$SCRIPT_DIR/$candidate"
        break
      fi
    done

    ICON_SRC="$SCRIPT_DIR/img/logo-droppdfcompress.svg"
    DESKTOP_SRC="$SCRIPT_DIR/DropPDFCompress.desktop"

    LOCAL_BIN_DIR="$HOME/.local/bin"
    LOCAL_APP_DIR="$HOME/.local/share/applications"
    LOCAL_ICON_DIR="$HOME/.local/share/icons/hicolor/scalable/apps"

    LAUNCHER_PATH="$LOCAL_BIN_DIR/$APP_ID"
    DESKTOP_PATH="$LOCAL_APP_DIR/$APP_ID.desktop"
    ICON_DEST="$LOCAL_ICON_DIR/$APP_ID.svg"

    mkdir -p "$LOCAL_BIN_DIR" "$LOCAL_APP_DIR" "$LOCAL_ICON_DIR"

    log() {
      printf '%s\n' "$*"
    }

    warn() {
      printf 'Attenzione: %s\n' "$*" >&2
    }

    find_python() {
      local candidates=(python3.13 python3.12 python3.11 python3.10 python3.9 python3.8 python3.7 python3)
      local py version major minor

      for py in "${candidates[@]}"; do
        if command -v "$py" >/dev/null 2>&1; then
          version="$($py -c 'import sys; print("%s.%s" % (sys.version_info[0], sys.version_info[1]))' 2>/dev/null)"
          major="${version%%.*}"
          minor="${version##*.}"
          if [ "$major" -gt 3 ] || { [ "$major" -eq 3 ] && [ "$minor" -ge 7 ]; }; then
            printf '%s' "$py"
            return 0
          fi
        fi
      done
      return 1
    }

    PYTHON_BIN="$(find_python)" || {
      warn "Nessun interprete Python compatibile trovato. Serve Python 3.7 o superiore."
      exit 1
    }

    if [ -z "$APP_SCRIPT" ]; then
      warn "File principale non trovato nella cartella: $SCRIPT_DIR"
      warn "Metti uno di questi file accanto allo script di installazione:"
      for candidate in "${CANDIDATES[@]}"; do
        warn "- $candidate"
      done
      exit 1
    fi

    chmod +x "$APP_SCRIPT" 2>/dev/null || true

    cat > "$LAUNCHER_PATH" <<EOF2
    #!/usr/bin/env bash
    cd "$SCRIPT_DIR" || exit 1
    exec "$PYTHON_BIN" "$APP_SCRIPT" "\$@"
    EOF2
    chmod +x "$LAUNCHER_PATH"

    if [ -f "$ICON_SRC" ]; then
      cp -f "$ICON_SRC" "$ICON_DEST"
    else
      warn "Icona non trovata: $ICON_SRC"
      warn "Creo comunque il launcher senza icona personalizzata."
    fi

    cat > "$DESKTOP_PATH" <<EOF2
    [Desktop Entry]
    Version=1.0
    Type=Application
    Name=$APP_NAME
    Comment=$APP_COMMENT
    Exec=$LAUNCHER_PATH
    Path=$SCRIPT_DIR
    Icon=$APP_ID
    Terminal=false
    StartupNotify=true
    Categories=Utility;Office;Graphics;
    Keywords=pdf;compress;compressione;converti;conversione;dragdrop;ghostscript;libreoffice;
    StartupWMClass=$APP_WM_CLASS
    EOF2
    chmod +x "$DESKTOP_PATH"

    # Compatibilità: aggiorna anche il file .desktop locale del progetto
    cp -f "$DESKTOP_PATH" "$DESKTOP_SRC" 2>/dev/null || true

    if command -v update-desktop-database >/dev/null 2>&1; then
      update-desktop-database "$LOCAL_APP_DIR" >/dev/null 2>&1 || true
    fi

    if command -v gtk-update-icon-cache >/dev/null 2>&1; then
      gtk-update-icon-cache "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
    fi

    if command -v xdg-desktop-menu >/dev/null 2>&1; then
      xdg-desktop-menu forceupdate >/dev/null 2>&1 || true
    fi

    DESKTOP_ENV_SUMMARY="${XDG_CURRENT_DESKTOP:-sconosciuto}"
    SESSION_TYPE_SUMMARY="${XDG_SESSION_TYPE:-sconosciuto}"

    log "Installazione completata."
    log ""
    log "Riepilogo:"
    log "- Script applicazione: $APP_SCRIPT"
    log "- Launcher: $LAUNCHER_PATH"
    log "- Desktop file: $DESKTOP_PATH"
    log "- Icona: $ICON_DEST"
    log "- Python usato: $PYTHON_BIN"
    log "- Desktop environment rilevato: $DESKTOP_ENV_SUMMARY"
    log "- Sessione: $SESSION_TYPE_SUMMARY"
    log ""
    log "Puoi avviare l'app dal menu come: $APP_NAME"
    log "Puoi avviare l'app anche da terminale con: $LAUNCHER_PATH"
    log ""
    log "Se l'icona non compare subito nel menu, esci e rientra nella sessione oppure riavvia il pannello/menu."
