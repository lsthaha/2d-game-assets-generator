#!/bin/bash
# 2D 游戏素材生成工具 - Linux/Mac 启动脚本

echo ""
echo "========================================"
echo "  2D 游戏素材生成工具 - 启动脚本"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] Python 3 未安装"
    echo "请访问 https://www.python.org/downloads/ 安装 Python 3.9+"
    exit 1
fi

python3 --version
echo "[✓] Python 已安装"
echo ""

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "[*] 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "[*] 激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "[*] 检查并安装依赖..."
pip install -q --upgrade pip setuptools wheel

echo "[*] 安装 PyTorch (CUDA 11.8)..."
pip install -q torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo "[*] 安装其他依赖..."
pip install -q -r requirements.txt

echo ""
echo "[✓] 依赖安装完成"
echo ""
echo "========================================"
echo "  启动选项"
echo "========================================"
echo ""
echo "选择要启动的服务："
echo "  1) 启动后端 (FastAPI)"
echo "  2) 启动前端 (Gradio)"
echo "  3) 同时启动后端和前端"
echo "  4) 检查后端健康状态"
echo "  0) 退出"
echo ""

read -p "请选择 (0-4): " choice

case $choice in
    1)
        echo ""
        echo "[*] 启动 FastAPI 后端服务..."
        echo "后端地址: http://127.0.0.1:8000"
        echo "API 文档: http://127.0.0.1:8000/docs"
        echo ""
        python backend/main.py
        ;;
    2)
        echo ""
        echo "[*] 启动 Gradio 前端应用..."
        echo "前端地址: http://127.0.0.1:7860"
        echo ""
        echo "[警告] 请确保后端已在另一个终端中运行！"
        echo ""
        python frontend/app.py
        ;;
    3)
        echo ""
        echo "[*] 在后台启动后端服务..."
        python backend/main.py > backend.log 2>&1 &
        BACKEND_PID=$!
        echo "[✓] 后端进程 ID: $BACKEND_PID"
        
        sleep 3
        
        echo "[*] 启动前端服务..."
        python frontend/app.py
        ;;
    4)
        echo ""
        echo "[*] 检查后端健康状态..."
        python3 -c "import requests; r=requests.get('http://127.0.0.1:8000/health'); print('✓ 后端在线' if r.status_code==200 else '✗ 后端离线')" 2>/dev/null
        if [ $? -ne 0 ]; then
            echo "[✗] 后端未运行，请先启动后端服务"
        fi
        echo ""
        ;;
    0)
        echo "[*] 退出"
        exit 0
        ;;
    *)
        echo "[错误] 无效选择"
        exit 1
        ;;
esac

deactivate
