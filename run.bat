@echo off
REM 2D 游戏素材生成工具 - Windows 启动脚本

echo.
echo ========================================
echo   2D 游戏素材生成工具 - Windows 启动
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Python 未安装或不在 PATH 中
    echo 请访问 https://www.python.org/downloads/ 安装 Python 3.9+
    pause
    exit /b 1
)

echo [✓] Python 已安装
echo.

REM 检查虚拟环境
if not exist "venv" (
    echo [*] 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo [*] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo [*] 检查并安装依赖...
pip install -q --upgrade pip setuptools wheel

REM 分别安装 PyTorch 和其他依赖（避免冲突）
echo [*] 安装 PyTorch (CUDA 11.8 版本)...
pip install -q torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo [*] 安装其他依赖...
pip install -q -r requirements.txt

echo.
echo [✓] 依赖安装完成
echo.
echo ========================================
echo   启动选项
echo ========================================
echo.
echo 选择要启动的服务：
echo   1) 启动后端 (FastAPI) - 仅后端
echo   2) 启动前端 (Gradio) - 仅前端
echo   3) 同时启动后端和前端
echo   4) 检查后端健康状态
echo   0) 退出
echo.

set /p choice="请选择 (0-4): "

if "%choice%"=="1" (
    echo.
    echo [*] 启动 FastAPI 后端服务...
    echo 后端地址: http://127.0.0.1:8000
    echo API 文档: http://127.0.0.1:8000/docs
    echo.
    python backend/main.py
) else if "%choice%"=="2" (
    echo.
    echo [*] 启动 Gradio 前端应用...
    echo 前端地址: http://127.0.0.1:7860
    echo.
    echo [警告] 请确保后端已在另一个窗口中运行！
    echo.
    python frontend/app.py
) else if "%choice%"=="3" (
    echo.
    echo [*] 将在两个新窗口中启动后端和前端...
    echo.
    start "2D 游戏素材生成 - 后端" cmd /k "call venv\Scripts\activate.bat && python backend/main.py"
    timeout /t 3 /nobreak
    echo [*] 后端窗口已启动，现在启动前端...
    echo.
    start "2D 游戏素材生成 - 前端" cmd /k "call venv\Scripts\activate.bat && python frontend/app.py"
    echo.
    echo [✓] 服务已启动！
    echo 后端: http://127.0.0.1:8000
    echo 前端: http://127.0.0.1:7860
    echo.
) else if "%choice%"=="4" (
    echo.
    echo [*] 检查后端健康状态...
    python -c "import requests; r=requests.get('http://127.0.0.1:8000/health'); print('✓ 后端在线' if r.status_code==200 else '✗ 后端离线')" 2>nul
    if %errorlevel% neq 0 (
        echo [✗] 后端未运行，请先启动后端服务
    )
    echo.
) else if "%choice%"=="0" (
    echo [*] 退出
    exit /b 0
) else (
    echo [错误] 无效选择
    exit /b 1
)

pause
