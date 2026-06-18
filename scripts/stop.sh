#!/usr/bin/env bash
# Para el backend de Advad.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$ROOT_DIR/.advad.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "No hay PID file, el backend no parece estar corriendo."
  exit 0
fi

PID="$(cat "$PID_FILE")"
if kill -0 "$PID" 2>/dev/null; then
  echo "Parando backend (PID $PID) ..."
  kill "$PID"
  echo "Backend detenido."
else
  echo "El proceso $PID ya no existe."
fi

rm -f "$PID_FILE"
