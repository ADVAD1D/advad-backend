#!/usr/bin/env bash
# Levanta el backend de Advad en segundo plano.
set -euo pipefail

# Carpeta raíz del proyecto (un nivel arriba de scripts/)
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PID_FILE="$ROOT_DIR/.advad.pid"
LOG_FILE="$ROOT_DIR/advad.log"
PORT="${PORT:-10000}"

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "El backend ya está corriendo (PID $(cat "$PID_FILE"))."
  exit 0
fi

echo "Levantando backend en http://0.0.0.0:$PORT ..."
PORT="$PORT" nohup uvicorn app.main:app --host 0.0.0.0 --port "$PORT" \
  > "$LOG_FILE" 2>&1 &

echo $! > "$PID_FILE"
echo "Backend iniciado (PID $(cat "$PID_FILE")). Logs en $LOG_FILE"
