# check_setup.py
import sys
from pathlib import Path

print("=" * 50)
print("检查项目结构")
print("=" * 50)

# 检查文件结构
required_files = [
    "backend/main.py",
    "backend/generators/sd_generator.py", 
    "backend/generators/background_remover.py",
    "backend/models/schemas.py",
    "config.py",
]

for f in required_files:
    exists = Path(f).exists()
    print(f"{'✓' if exists else '✗'} {f}")

print("\n" + "=" * 50)
print("检查导入")
print("=" * 50)

try:
    from config import MODEL_CONFIG
    print("✓ config.py 导入成功")
except Exception as e:
    print(f"✗ config.py 导入失败: {e}")

try:
    from backend.models.schemas import GenerationRequest
    print("✓ schemas.py 导入成功")
except Exception as e:
    print(f"✗ schemas.py 导入失败: {e}")

try:
    from backend.generators.sd_generator import create_generator
    print("✓ sd_generator.py 导入成功")
except Exception as e:
    print(f"✗ sd_generator.py 导入失败: {e}")

try:
    from backend.generators.background_remover import BackgroundRemover
    print("✓ background_remover.py 导入成功")
except Exception as e:
    print(f"✗ background_remover.py 导入失败: {e}")

print("\n" + "=" * 50)
print("检查依赖")
print("=" * 50)

packages = ["fastapi", "gradio", "torch", "PIL"]
for pkg in packages:
    try:
        __import__(pkg)
        print(f"✓ {pkg}")
    except ImportError:
        print(f"✗ {pkg} 未安装")