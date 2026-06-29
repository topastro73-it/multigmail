#!/usr/bin/env bash
# Setup manuale (opzionale): crea il venv e installa le dipendenze in anticipo,
# così il primo avvio del server è immediato. Equivalente a ensure_deps.sh ma
# pensato per essere lanciato a mano dopo il clone/installazione.
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
"$DIR/scripts/ensure_deps.sh"
echo "[multigmail] Dipendenze installate in $DIR/.venv"
echo "[multigmail] Ricorda di mettere le credenziali OAuth in ~/.multigmail/credentials.json (vedi README)."
