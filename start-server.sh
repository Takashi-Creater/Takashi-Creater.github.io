#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8000}"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$ROOT_DIR/.local_server.pid"
LOG_FILE="$ROOT_DIR/.local_server.log"

# 画像チェック関数
check_and_download_images() {
  echo "画像をチェック中..."
  
  # sweetsの画像チェック
  if [[ ! -d "$ROOT_DIR/sweets/images" ]] || [[ $(ls -1 "$ROOT_DIR/sweets/images/"*.jpg 2>/dev/null | wc -l) -lt 10 ]]; then
    echo "sweets画像が不足しています。ダウンロード中..."
    cd "$ROOT_DIR/sweets"
    python download_images.py
    cd "$ROOT_DIR"
  else
    echo "✓ sweets画像は完全です"
  fi
  
  # travelの画像チェック
  if [[ ! -d "$ROOT_DIR/travel/images" ]] || [[ $(ls -1 "$ROOT_DIR/travel/images/"*.jpg 2>/dev/null | wc -l) -lt 10 ]]; then
    echo "travel画像が不足しています。ダウンロード中..."
    cd "$ROOT_DIR/travel"
    python download_images.py
    cd "$ROOT_DIR"
  else
    echo "✓ travel画像は完全です"
  fi
  
  echo "画像チェック完了"
}

if [[ -f "$PID_FILE" ]] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "Server already running (pid $(cat "$PID_FILE"))"
  exit 0
fi

# サーバー起動前に画像をチェック
check_and_download_images

cd "$ROOT_DIR"
nohup python -m http.server "$PORT" >"$LOG_FILE" 2>&1 &
echo $! >"$PID_FILE"

echo "Server started on http://localhost:$PORT (pid $(cat "$PID_FILE"))"
