"""
全局配置 - 2D 游戏素材生成工具
"""
import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent

# 输出目录
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

# 缓存目录
CACHE_DIR = BASE_DIR / "cache"
CACHE_DIR.mkdir(exist_ok=True)

# 模型配置 (Intel Mac - CPU优化模式)
MODEL_CONFIG = {
    "base_model": "runwayml/stable-diffusion-v1-5",
    "lcm_lora": "latent-consistency/lcm-lora-sdv1-5",  # LCM 加速,CPU也能2-3分钟生成
    "device": "cpu",  # Intel Mac使用CPU (AMD GPU不支持PyTorch)
    "dtype": "float32",  # CPU模式使用float32
    "enable_attention_slicing": True,  # CPU内存优化
    "enable_memory_efficient_attention": False,  # CPU不需要
    "background_removal_method": "rembg",
}

# 生成参数预设
GENERATION_PRESETS = {
    "character_portrait": {
        "width": 512,
        "height": 512,
        "guidance_scale": 7.5,
        "num_inference_steps": 4,  # LCM使用4步 (CPU约2-3分钟,GPU约2-3秒)
        "style_lora": None,
    },
    "character_sprite_4way": {
        "width": 128,
        "height": 128,
        "guidance_scale": 7.5,
        "num_inference_steps": 8,
        "style_lora": None,
    },
    "background": {
        "width": 1024,
        "height": 768,
        "guidance_scale": 5.0,
        "num_inference_steps": 8,
        "style_lora": None,
    },
    "tileset": {
        "width": 256,
        "height": 256,
        "guidance_scale": 7.0,
        "num_inference_steps": 8,
        "style_lora": None,
    },
    "ui_icon": {
        "width": 256,
        "height": 256,
        "guidance_scale": 7.5,
        "num_inference_steps": 8,
        "style_lora": None,
    },
}

# 后处理配置
POSTPROCESS_CONFIG = {
    "enable_background_removal": True,
    "background_removal_method": "rembg",  # rembg 或 sam
    "enable_upscale": False,
    "upscale_factor": 2,
}

# FastAPI 配置
API_CONFIG = {
    "host": "127.0.0.1",
    "port": 8001,
    "reload": True,
    "workers": 1,  # GPU 通常只用 1 个 worker
}

# 提示词模板
PROMPT_TEMPLATES = {
    "pixel_art_character": "2d pixel art game character, {description}, no background, standing pose, game sprite, high quality",
    "cartoon_character": "2d cartoon game character, {description}, colorful, simple style, no background, game asset",
    "hand_drawn_character": "2d hand drawn game character, {description}, ink style, expressive, no background",
    "flat_design_character": "2d flat design game character, {description}, minimalist, vector style, no background",
    "background_scene": "2d game background scene, {description}, isometric view, layered, game asset quality",
    "tileset_ground": "2d seamless tileset texture, {description}, game ground tiles, 256x256, tileable pattern",
    "ui_icon": "simple 2d game icon, {description}, flat design, 256x256, clear outline, white background",
}

# 日志配置
LOG_LEVEL = "INFO"
LOG_FILE = BASE_DIR / "logs" / "app.log"
LOG_FILE.parent.mkdir(exist_ok=True)

# ==================== 七牛云企业级配置 ====================

# 七牛云Kodo配置
QINIU_CONFIG = {
    "enabled": False,  # 是否启用七牛云集成
    "access_key": os.getenv("QINIU_ACCESS_KEY", ""),  # 从环境变量读取
    "secret_key": os.getenv("QINIU_SECRET_KEY", ""),
    "bucket_name": os.getenv("QINIU_BUCKET", "game-assets-prod"),
    "cdn_domain": os.getenv("QINIU_CDN_DOMAIN", "assets.yourgame.com"),
    "region": os.getenv("QINIU_REGION", "z0"),  # z0=华东, z1=华北, z2=华南
    "use_https": True,
    "private_access": True,  # 是否使用私有访问
}

# 风格缓存配置
STYLE_CACHE_CONFIG = {
    "enabled": True,  # 是否启用风格缓存
    "cache_dir": CACHE_DIR / "styles",
    "default_ttl_days": 30,  # 默认缓存有效期(天)
    "max_cache_size_mb": 5000,  # 最大缓存大小(MB)
    "sync_to_kodo": False,  # 是否自动同步到Kodo (需启用QINIU_CONFIG)
    "prefetch_enabled": False,  # 是否启用预取
}

# 项目管理配置
PROJECT_CONFIG = {
    "default_project_name": "Default Project",
    "metadata_format": "json",  # json 或 yaml
    "auto_backup": True,  # 是否自动备份配置
}

# CDN缓存策略
CDN_CACHE_STRATEGY = {
    "asset_images": {
        "pattern": "*.png,*.jpg",
        "ttl_days": 30,
        "refresh": "url"  # url 或 directory
    },
    "metadata": {
        "pattern": "*.json",
        "ttl_days": 1,
        "refresh": "directory"
    },
    "style_templates": {
        "pattern": "/styles/**",
        "ttl_days": 7,
        "prefetch": True
    }
}
