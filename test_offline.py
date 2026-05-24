"""
离线测试脚本 - 不需要启动 FastAPI 和 Gradio，直接测试生成器
用于快速验证和调试
"""
import sys
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_generator_offline():
    """测试 SD 生成器（离线模式）"""
    print("\n" + "="*60)
    print("  测试 Stable Diffusion 生成器 (离线模式)")
    print("="*60 + "\n")
    
    try:
        from backend.generators.sd_generator import create_generator
        from config import MODEL_CONFIG, OUTPUT_DIR
        
        logger.info("创建生成器实例...")
        generator = create_generator(
            device=MODEL_CONFIG.get("device", "cuda"),
            dtype=MODEL_CONFIG.get("dtype", "float16"),
        )
        
        # 生成占位符图像 (因为模型可能未安装)
        logger.info("生成测试图像 (占位符)...")
        output_dir = OUTPUT_DIR / "test"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        image = generator.generate(
            prompt="a knight warrior",
            width=256,
            height=256,
            num_inference_steps=4,
            output_path=output_dir / "test_character.png"
        )
        
        logger.info(f"✓ 生成成功: {output_dir / 'test_character.png'}")
        logger.info(f"  图像大小: {image.size}")
        
        return True
    
    except Exception as e:
        logger.error(f"✗ 生成失败: {e}")
        return False


def test_background_remover_offline():
    """测试背景移除器（离线模式）"""
    print("\n" + "="*60)
    print("  测试背景移除器 (离线模式)")
    print("="*60 + "\n")
    
    try:
        from backend.generators.background_remover import BackgroundRemover
        from config import OUTPUT_DIR
        from PIL import Image
        import numpy as np
        
        logger.info("创建背景移除器实例...")
        remover = BackgroundRemover(method="rembg")
        
        # 创建测试图像
        logger.info("创建测试图像...")
        test_image = Image.new("RGB", (256, 256), color=(255, 100, 100))
        output_dir = OUTPUT_DIR / "test"
        output_dir.mkdir(parents=True, exist_ok=True)
        test_image_path = output_dir / "test_image.png"
        test_image.save(test_image_path)
        
        logger.info("进行背景移除...")
        result = remover.remove_background(test_image_path)
        
        logger.info(f"✓ 背景移除成功: {result.size}, 模式: {result.mode}")
        
        # 保存结果
        result.save(output_dir / "test_transparent.png")
        logger.info(f"  已保存到: {output_dir / 'test_transparent.png'}")
        
        return True
    
    except Exception as e:
        logger.error(f"✗ 背景移除失败: {e}")
        return False


def test_api_endpoints():
    """测试 API 端点连接（需要后端运行）"""
    print("\n" + "="*60)
    print("  测试 API 端点")
    print("="*60 + "\n")
    
    try:
        import requests
        
        base_url = "http://127.0.0.1:8000"
        
        # 健康检查
        logger.info(f"检查 {base_url}...")
        response = requests.get(f"{base_url}/health", timeout=5)
        
        if response.status_code == 200:
            logger.info("✓ 后端在线")
            data = response.json()
            logger.info(f"  生成器状态: {data['services']['generator']}")
            logger.info(f"  计算设备: {data['gpu']['device']}")
            return True
        else:
            logger.warning(f"✗ 后端返回状态码 {response.status_code}")
            return False
    
    except requests.exceptions.ConnectionError:
        logger.warning("✗ 无法连接到后端 (这是正常的，如果你还没启动后端)")
        logger.info("  提示: 运行 'python backend/main.py' 启动后端")
        return False
    except Exception as e:
        logger.error(f"✗ API 测试失败: {e}")
        return False


def test_data_models():
    """测试数据模型"""
    print("\n" + "="*60)
    print("  测试数据模型")
    print("="*60 + "\n")
    
    try:
        from backend.models.schemas import (
            GenerationRequest,
            GenerationResponse,
            TaskStatus,
        )
        
        logger.info("创建生成请求...")
        request = GenerationRequest(
            prompt="test character",
            asset_type="character_portrait",
            style="pixel_art",
        )
        logger.info(f"✓ 请求创建成功: {request.prompt}")
        
        logger.info("创建生成响应...")
        response = GenerationResponse(
            task_id="test-123",
            image_paths=["/output/test.png"],
        )
        logger.info(f"✓ 响应创建成功: {response.status}")
        
        logger.info("创建任务状态...")
        status = TaskStatus(
            task_id="test-123",
            status="completed",
            progress=100.0,
            message="测试成功",
        )
        logger.info(f"✓ 状态创建成功: {status.status}")
        
        return True
    
    except Exception as e:
        logger.error(f"✗ 数据模型测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("\n")
    print("█" * 60)
    print("█  2D 游戏素材生成工具 - 离线测试")
    print("█" * 60)
    
    results = {}
    
    # 运行测试
    results["数据模型"] = test_data_models()
    results["生成器 (离线)"] = test_generator_offline()
    results["背景移除器 (离线)"] = test_background_remover_offline()
    results["API 端点"] = test_api_endpoints()
    
    # 总结
    print("\n" + "="*60)
    print("  测试总结")
    print("="*60 + "\n")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败/跳过"
        print(f"{test_name:20} {status}")
    
    print(f"\n总计: {passed}/{total} 通过\n")
    
    if passed >= total - 1:  # 允许 API 测试失败
        print("✓ 大部分测试通过！")
        print("\n下一步:")
        print("  1. 运行 'python backend/main.py' 启动后端")
        print("  2. 运行 'python frontend/app.py' 启动前端")
        print("  3. 打开 http://127.0.0.1:7860 开始生成素材")
        return 0
    else:
        print("✗ 某些测试失败，请检查安装和配置")
        return 1


if __name__ == "__main__":
    sys.exit(main())
