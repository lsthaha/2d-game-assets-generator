#!/usr/bin/env python3
"""
后端服务启动脚本 - 用于 Colab 和本地环境
确保正确的 Python 路径设置
"""
import sys
from pathlib import Path

# 确保项目根目录在 Python 路径中
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print(f"✓ 项目根目录: {project_root}")
print(f"✓ Python 路径已配置")
print(f"✓ 启动后端服务...\n")

# 直接导入并运行
if __name__ == "__main__":
    # 导入配置
    from config import API_CONFIG
    
    # 导入 FastAPI app
    from backend.main import app
    
    # 导入 uvicorn
    import uvicorn
    
    # 运行服务
    uvicorn.run(
        app,
        host=API_CONFIG.get("host", "0.0.0.0"),
        port=API_CONFIG.get("port", 8001),
        log_level="info"
    )
