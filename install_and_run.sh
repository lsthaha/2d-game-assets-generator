#!/bin/bash
# 2D游戏素材生成工具 - 自动安装和运行脚本

echo "================================================"
echo "  2D游戏素材生成工具 - 自动安装"
echo "================================================"
echo ""

# 1. 激活conda环境
echo "步骤 1/5: 激活conda环境..."
source ~/.zshrc
conda activate game-assets

# 2. 安装PyTorch (使用conda)
echo ""
echo "步骤 2/5: 安装PyTorch (这可能需要5-10分钟)..."
conda install pytorch torchvision cpuonly -c pytorch -y

# 3. 安装其他依赖
echo ""
echo "步骤 3/5: 安装其他依赖..."
cd /Users/mac/Desktop/2d
pip install diffusers==0.24.0 transformers==4.35.0
pip install gradio==4.11.0 fastapi==0.104.1 uvicorn==0.24.0
pip install rembg pillow opencv-python pyyaml python-dotenv
pip install peft safetensors requests pydantic qiniu

# 4. 检查安装
echo ""
echo "步骤 4/5: 检查安装..."
python -c "import torch; print(f'PyTorch版本: {torch.__version__}'); print(f'设备: CPU模式')"
python -c "import diffusers; print(f'Diffusers版本: {diffusers.__version__}')"
python -c "import gradio; print(f'Gradio版本: {gradio.__version__}')"

# 5. 运行说明
echo ""
echo "================================================"
echo "  安装完成! ✅"
echo "================================================"
echo ""
echo "运行方式:"
echo ""
echo "方式1: 同时启动后端和前端"
echo "  ./run.sh"
echo "  选择: 3"
echo ""
echo "方式2: 分别启动"
echo "  # 终端1 (后端)"
echo "  conda activate game-assets"
echo "  python backend/main.py"
echo ""
echo "  # 终端2 (前端)"
echo "  conda activate game-assets"
echo "  python frontend/app.py"
echo ""
echo "访问地址:"
echo "  前端: http://127.0.0.1:7860"
echo "  后端: http://127.0.0.1:8001"
echo ""
echo "⚠️  注意:"
echo "  - CPU模式生成时间: 2-4分钟/张"
echo "  - 首次运行会下载模型 (约5GB)"
echo "  - 请确保有足够的磁盘空间和内存"
echo ""
