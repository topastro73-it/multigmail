#!/usr/bin/env bash
# Launcher dell'MCP server MultiGmail.
# Si auto-configura al primo avvio (crea venv + installa dipendenze), poi
# avvia il server. Funziona sia come plugin installato (CLAUDE_PLUGIN_ROOT)
# sia in sviluppo locale.
set -euo pipefail

ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"

"$ROOT/scripts/ensure_deps.sh"

exec "$ROOT/.venv/bin/python" "$ROOT/src/server.py"
