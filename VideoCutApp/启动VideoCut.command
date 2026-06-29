#!/bin/bash
set -e

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$APP_DIR/.." && pwd)"
PYTHON="/Users/zzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"

if [ ! -x "$PYTHON" ]; then
  PYTHON="$(command -v python3)"
fi

if [ -z "$PYTHON" ]; then
  echo "未找到 Python。请在 Codex 环境里运行，或先安装 Python 3。"
  if [ -t 0 ]; then
    read -r -p "按回车退出..."
  fi
  exit 1
fi

cd "$PROJECT_DIR"
echo "启动 VideoCut..."
echo "项目目录：$PROJECT_DIR"
echo "浏览器地址：http://127.0.0.1:8765"

if command -v lsof >/dev/null 2>&1; then
  OLD_PIDS="$(lsof -tiTCP:8765 -sTCP:LISTEN || true)"
  if [ -n "$OLD_PIDS" ]; then
    echo "检测到 8765 端口已有旧服务，正在清理..."
    kill $OLD_PIDS >/dev/null 2>&1 || true
    sleep 1
  fi
fi

if command -v open >/dev/null 2>&1; then
  (sleep 1 && open "http://127.0.0.1:8765") >/dev/null 2>&1 &
fi

"$PYTHON" -m webapp.server
