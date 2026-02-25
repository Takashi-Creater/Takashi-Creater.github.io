#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$ROOT_DIR/.local_server.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "No pid file found. Server may not be running."
  exit 0
fi

PID="$(cat "$PID_FILE")"
if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  echo "Server stopped (pid $PID)"
else
  echo "Process not running (pid $PID)"
fi

rm -f "$PID_FILE"
