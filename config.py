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

# 模型配置
MODEL_CONFIG = {
    "base_model": "runwayml/stable-diffusion-v1-5",  # 或 stabilityai/stable-diffusion-xl-base-1.0
    "lcm_lora": "latent-consistency/lcm-lora-sdv1-5",  # LCM LoRA 用于加速
    "device": "cpu",  # cuda 或 cpu
    "dtype": "float32",  # float16 或 float32
    "enable_attention_slicing": False,  # CPU模式不需要
    "enable_memory_efficient_attention": False,  # CPU模式不需要
    "background_removal_method": "rembg",  # 保持不变
}

# 生成参数预设
GENERATION_PRESETS = {
    "character_portrait": {
        "width": 512,
        "height": 512,
        "guidance_scale": 7.5,
        "num_inference_steps": 8,  # LCM 使用较少步数
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
