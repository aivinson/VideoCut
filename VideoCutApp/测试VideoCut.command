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
echo "运行单元测试..."
"$PYTHON" -m unittest discover -s tests

echo
echo "运行 dry-run..."
"$PYTHON" -m harness.run --brief inputs/brief.example.json --dry-run

echo
echo "测试完成。"
if [ -t 0 ]; then
  read -r -p "按回车退出..."
fi
