"""
简单测试脚本 - 验证系统是否正确安装
"""
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试所有必要的导入"""
    print("🔍 检查导入依赖...")
    
    tests = [
        ("config", "配置模块"),
        ("fastapi", "FastAPI"),
        ("gradio", "Gradio"),
        ("PIL", "Pillow"),
        ("torch", "PyTorch"),
    ]
    
    failed = []
    
    for module_name, display_name in tests:
        try:
            __import__(module_name)
            print(f"  ✓ {display_name}")
        except ImportError as e:
            print(f"  ✗ {display_name} - {e}")
            failed.append(display_name)
    
    return len(failed) == 0, failed


def test_directories():
    """测试目录结构"""
    print("\n🔍 检查目录结构...")
    
    required_dirs = [
        "backend/generators",
        "backend/models",
        "backend/utils",
        "frontend",
        "output",
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"  ✓ {dir_path}/")
        else:
            print(f"  ✗ {dir_path}/ 不存在")
            all_exist = False
    
    return all_exist


def test_files():
    """测试文件是否存在"""
    print("\n🔍 检查文件...")
    
    required_files = [
        "config.py",
        "requirements.txt",
        "backend/main.py",
        "backend/generators/sd_generator.py",
        "backend/generators/background_remover.py",
        "backend/models/schemas.py",
        "frontend/app.py",
        "README.md",
    ]
    
    all_exist = True
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"  ✓ {file_path} ({size:,} 字节)")
        else:
            print(f"  ✗ {file_path} 不存在")
            all_exist = False
    
    return all_exist


def test_config():
    """测试配置是否可加载"""
    print("\n🔍 检查配置...")
    
    try:
        from config import (
            MODEL_CONFIG,
            GENERATION_PRESETS,
            PROMPT_TEMPLATES,
            API_CONFIG,
        )
        
        print(f"  ✓ 基础模型: {MODEL_CONFIG.get('base_model')}")
        print(f"  ✓ LCM LoRA: {MODEL_CONFIG.get('lcm_lora')}")
        print(f"  ✓ 计算设备: {MODEL_CONFIG.get('device')}")
        print(f"  ✓ 生成预设: {len(GENERATION_PRESETS)} 个")
        print(f"  ✓ 提示词模板: {len(PROMPT_TEMPLATES)} 个")
        print(f"  ✓ API 地址: http://{API_CONFIG['host']}:{API_CONFIG['port']}")
        
        return True
    except Exception as e:
        print(f"  ✗ 配置加载失败: {e}")
        return False


def test_models():
    """测试模型是否可导入"""
    print("\n🔍 检查模型导入...")
    
    try:
        from backend.generators.sd_generator import create_generator
        from backend.generators.background_remover import BackgroundRemover
        from backend.models.schemas import GenerationRequest, GenerationResponse
        
        print("  ✓ SD 生成器")
        print("  ✓ 背景移除器")
        print("  ✓ 数据模型")
        
        return True
    except Exception as e:
        print(f"  ✗ 模型导入失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n" + "="*50)
    print("  2D 游戏素材生成工具 - 系统检查")
    print("="*50 + "\n")
    
    results = []
    
    # 运行测试
    results.append(("导入依赖", test_imports()[0]))
    results.append(("目录结构", test_directories()))
    results.append(("文件完整性", test_files()))
    results.append(("配置加载", test_config()))
    results.append(("模型导入", test_models()))
    
    # 总结
    print("\n" + "="*50)
    print("  测试总结")
    print("="*50 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:15} {status}")
    
    print(f"\n总计: {passed}/{total} 通过\n")
    
    if passed == total:
        print("✓ 系统检查完成，所有组件就绪！")
        print("\n现在可以启动服务：")
        print("  Windows: run.bat")
        print("  Linux/Mac: ./run.sh")
        return 0
    else:
        print("✗ 某些组件缺失，请检查安装")
        return 1


if __name__ == "__main__":
    sys.exit(main())
