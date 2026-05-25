#!/bin/bash
# 后端启动脚本 - Colab 专用

cd "$(dirname "$0")"

echo "✓ 工作目录: $(pwd)"
echo "✓ 设置 PYTHONPATH..."

export PYTHONPATH="$(pwd):${PYTHONPATH}"

echo "✓ PYTHONPATH=${PYTHONPATH}"
echo "✓ 启动后端服务..."
echo ""

# 使用 uvicorn 命令行方式启动
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8001
