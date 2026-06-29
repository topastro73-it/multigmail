#!/usr/bin/env bash
# Crea il virtualenv e installa le dipendenze del plugin se non già presenti.
# Idempotente e veloce: se il venv esiste già ed è valido, esce subito.
set -euo pipefail

ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
VENV="$ROOT/.venv"
PY="$VENV/bin/python"

# Già pronto? Niente da fare (e stdout resta pulito per il protocollo MCP).
if [ -x "$PY" ] && "$PY" -c "import mcp, googleapiclient" >/dev/null 2>&1; then
  exit 0
fi

# Serve Python >= 3.10 (richiesto dal pacchetto `mcp`). L'alias `python3` non
# vale negli script non interattivi, dove spesso punta al Python di sistema più
# vecchio: quindi cerchiamo esplicitamente un interprete adatto.
pick_python() {
  local candidates=("${MULTIGMAIL_PYTHON:-}" python3.13 python3.12 python3.11 python3.10 python3)
  for c in "${candidates[@]}"; do
    [ -z "$c" ] && continue
    if command -v "$c" >/dev/null 2>&1 && \
       "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)' 2>/dev/null; then
      command -v "$c"
      return 0
    fi
  done
  return 1
}

PYTHON="$(pick_python)" || {
  echo "[multigmail] Serve Python >= 3.10 ma non l'ho trovato. Installa Python 3.10+ (es. 'brew install python@3.12') oppure imposta MULTIGMAIL_PYTHON al percorso giusto." >&2
  exit 1
}

# IMPORTANTE: tutto l'output va su stderr. Lo stdout deve restare pulito perché
# è il canale del protocollo MCP (JSON-RPC) quando il launcher avvia il server.
echo "[multigmail] Configuro l'ambiente con $PYTHON ..." >&2
rm -rf "$VENV"
"$PYTHON" -m venv "$VENV" >&2
"$VENV/bin/pip" install -q --upgrade pip >/dev/null 2>&1 || true
"$VENV/bin/pip" install -q -r "$ROOT/src/requirements.txt" >&2
