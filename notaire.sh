#!/bin/bash
# NotaireAI - Script Bash pour Linux/Mac
#
# Usage:
#   ./notaire.sh
#   ./notaire.sh --quick
#   ./notaire.sh --type vente -d donnees.json
#
# Version: 1.3.0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"

exec "$PYTHON" "$SCRIPT_DIR/generer_acte.py" "$@"
