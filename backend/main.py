"""
FastAPI 后端主应用 - 2D 游戏素材生成服务
"""
import logging
import uuid
from pathlib import Path
from typing import Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 导入本地模块
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import OUTPUT_DIR, API_CONFIG, MODEL_CONFIG, PROMPT_TEMPLATES
from backend.models.schemas import GenerationRequest, GenerationResponse, TaskStatus
from backend.generators.sd_generator import create_generator
from backend.generators.background_remover import BackgroundRemover

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局状态
class AppState:
    def __init__(self):
        self.generator = None
        self.background_remover = None
        self.tasks = {}  # task_id -> task_status
        self.executor = ThreadPoolExecutor(max_workers=1)  # 单个 GPU worker

app_state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动事件
    logger.info("========== 2D 游戏素材生成工具启动 ==========")
    logger.info("正在初始化 AI 模型...")
    
    try:
        # 初始化 Stable Diffusion 生成器
        app_state.generator = create_generator(
            model_id=MODEL_CONFIG.get("base_model", "runwayml/stable-diffusion-v1-5"),
            lcm_lora_id=MODEL_CONFIG.get("lcm_lora", "latent-consistency/lcm-lora-sdv1-5"),
            device=MODEL_CONFIG.get("device", "cuda"),
            dtype=MODEL_CONFIG.get("dtype", "float16"),
        )
        
        # 初始化背景移除器
        app_state.background_remover = BackgroundRemover(
            method=MODEL_CONFIG.get("background_removal_method", "rembg")
        )
        
        logger.info("✓ 模型初始化完成")
        logger.info(f"✓ 输出目录: {OUTPUT_DIR}")
        logger.info(f"✓ 服务地址: http://{API_CONFIG['host']}:{API_CONFIG['port']}")
        logger.info(f"✓ API 文档: http://{API_CONFIG['host']}:{API_CONFIG['port']}/docs")
        
    except Exception as e:
        logger.error(f"✗ 模型初始化失败: {e}")
        logger.warning("将在离线模式下运行")
    
    # 应用运行期间
    yield
    
    # 关闭事件
    logger.info("正在关闭应用...")
    app_state.executor.shutdown(wait=True)


# 初始化 FastAPI 应用，使用 lifespan
app = FastAPI(
    title="2D 游戏素材生成工具",
    description="高效、低成本的 AI 游戏素材生成服务",
    version="0.2.0-MVP",
    lifespan=lifespan,
)

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    """健康检查"""
    return {
        "status": "ok",
        "service": "2D 游戏素材生成工具",
        "version": "0.2.0-MVP",
        "generator_ready": app_state.generator is not None and app_state.generator.is_ready,
    }


@app.post("/generate", response_model=GenerationResponse, tags=["Generation"])
async def generate_asset(
    request: GenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    生成游戏素材
    
    - **prompt**: 素材描述提示词
    - **asset_type**: 素材类型 (character_portrait, background, tileset, ui_icon)
    - **style**: 风格 (pixel_art, cartoon, hand_drawn, flat)
    - **remove_background**: 是否自动抠图
    """
    
    if not app_state.generator:
        raise HTTPException(status_code=503, detail="生成服务未就绪")
    
    task_id = str(uuid.uuid4())[:8]
    output_dir = OUTPUT_DIR / task_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "generated.png"
    transparent_path = output_dir / "generated_transparent.png"
    
    try:
        # 构建完整提示词
        style_prefix = PROMPT_TEMPLATES.get(f"{request.style}_character", "")
        full_prompt = f"{style_prefix.format(description=request.prompt)}" if "{description}" in style_prefix else request.prompt
        
        logger.info(f"[{task_id}] 任务开始 - 类型: {request.asset_type}, 风格: {request.style}")
        logger.info(f"[{task_id}] 提示词: {full_prompt}")
        
        # 生成图像
        image = app_state.generator.generate(
            prompt=full_prompt,
            negative_prompt=request.negative_prompt,
            width=request.width,
            height=request.height,
            guidance_scale=request.guidance_scale,
            num_inference_steps=request.num_inference_steps,
            seed=request.seed,
            output_path=output_path,
        )
        actual_seed = getattr(app_state.generator, "last_seed", request.seed)
        
        # 抠图处理
        final_image_path = output_path
        if request.remove_background and app_state.background_remover:
            logger.info(f"[{task_id}] 执行背景移除...")
            transparent_image = app_state.background_remover.remove_background(image)
            transparent_image.save(transparent_path, "PNG")
            final_image_path = transparent_path
            logger.info(f"[{task_id}] 背景移除完成: {transparent_path}")
        
        # 保存元数据
        metadata_path = output_dir / "metadata.json"
        import json
        metadata = {
            "task_id": task_id,
            "prompt": full_prompt,
            "negative_prompt": request.negative_prompt,
            "asset_type": request.asset_type,
            "style": request.style,
            "width": request.width,
            "height": request.height,
            "guidance_scale": request.guidance_scale,
            "num_inference_steps": request.num_inference_steps,
            "seed": actual_seed,
            "remove_background": request.remove_background,
        }
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"[{task_id}] 任务完成")
        
        # 返回响应
        return GenerationResponse(
            status="success",
            task_id=task_id,
            image_paths=[str(final_image_path)],
            seed=actual_seed,
            metadata={
                "prompt": full_prompt,
                "style": request.style,
                "asset_type": request.asset_type,
                "seed": actual_seed,
            }
        )
        
    except Exception as e:
        logger.error(f"[{task_id}] 生成失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成失败: {str(e)}")
    
@app.get("/task/{task_id}", response_model=TaskStatus, tags=["Task"])
async def get_task_status(task_id: str):
    """查询任务状态"""
    if task_id not in app_state.tasks:
        return TaskStatus(
            task_id=task_id,
            status="unknown",
            progress=0,
            message="任务不存在"
        )
    
    return app_state.tasks[task_id]


@app.get("/image/{task_id}", tags=["Images"])
async def get_generated_image(task_id: str, format: str = "transparent"):
    """
    下载生成的图像
    
    - **format**: "transparent" (抠图) 或 "original" (原始)
    """
    output_dir = OUTPUT_DIR / task_id
    
    if format == "transparent":
        image_path = output_dir / "generated_transparent.png"
    else:
        image_path = output_dir / "generated.png"
    
    if not image_path.exists():
        raise HTTPException(status_code=404, detail="图像不存在")
    
    return FileResponse(image_path, media_type="image/png")


@app.get("/styles", tags=["Styles"])
async def get_available_styles():
    """获取可用的风格列表"""
    return {
        "styles": [
            {
                "id": "pixel_art",
                "name": "像素风格",
                "description": "复古像素艺术风格，适合像素类游戏"
            },
            {
                "id": "cartoon",
                "name": "卡通风格",
                "description": "明亮欢快的卡通风格"
            },
            {
                "id": "hand_drawn",
                "name": "手绘风格",
                "description": "温暖的手工绘制风格"
            },
            {
                "id": "flat",
                "name": "扁平设计",
                "description": "现代扁平设计风格"
            }
        ]
    }


@app.get("/asset-types", tags=["Assets"])
async def get_asset_types():
    """获取支持的素材类型"""
    return {
        "asset_types": [
            {
                "id": "character_portrait",
                "name": "角色立绘",
                "description": "生成单个角色的立绘或头像",
                "default_width": 512,
                "default_height": 512,
            },
            {
                "id": "character_sprite",
                "name": "角色精灵",
                "description": "生成游戏角色的精灵图（多帧/多向）",
                "default_width": 128,
                "default_height": 128,
            },
            {
                "id": "background",
                "name": "场景背景",
                "description": "生成游戏场景或背景",
                "default_width": 1024,
                "default_height": 768,
            },
            {
                "id": "tileset",
                "name": "瓦片地图",
                "description": "生成无缝拼接的瓦片纹理",
                "default_width": 256,
                "default_height": 256,
            },
            {
                "id": "ui_icon",
                "name": "UI图标",
                "description": "生成游戏UI元素或图标",
                "default_width": 256,
                "default_height": 256,
            },
        ]
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """详细的健康检查"""
    return {
        "status": "healthy",
        "services": {
            "generator": "ready" if app_state.generator and app_state.generator.is_ready else "not_ready",
            "background_remover": "ready" if app_state.background_remover else "not_ready",
        },
        "gpu": {
            "available": False if MODEL_CONFIG.get("device") == "cpu" else True,
            "device": MODEL_CONFIG.get("device"),
        }
    }


if __name__ == "__main__":
    logger.info("启动 FastAPI 服务器...")
    uvicorn.run(
        app,
        host=API_CONFIG["host"],
        port=API_CONFIG["port"],
        reload=False,
        log_level="info",
    )
