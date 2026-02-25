#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8000}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$ROOT_DIR/.local_server.pid"
LOG_FILE="$ROOT_DIR/.local_server.log"

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "Server already running (pid $(cat "$PID_FILE"))"
  exit 0
fi

cd "$ROOT_DIR"
nohup python -m http.server "$PORT" >"$LOG_FILE" 2>&1 &
echo $! >"$PID_FILE"

echo "Server started on http://localhost:$PORT (pid $(cat "$PID_FILE"))"
