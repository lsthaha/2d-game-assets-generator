#!/usr/bin/env python3
"""
Colab 专用后端启动文件 - 简化版
直接在项目根目录运行，无需复杂的模块导入配置
"""
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

print(f"✓ 项目根目录: {project_root}")
print(f"✓ Python 路径: {sys.path[0]}")
print(f"✓ 启动后端服务...\n")

# 现在可以直接导入了
if __name__ == "__main__":
    import uvicorn
    
    # 导入 app (此时 sys.path 已正确设置)
    from backend.main import app
    from config import API_CONFIG
    
    # 启动服务
    uvicorn.run(
        app,
        host=API_CONFIG.get("host", "0.0.0.0"),
        port=API_CONFIG.get("port", 8001),
        log_level="info"
    )
