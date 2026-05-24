"""
Stable Diffusion + LCM 生成器 - 核心图像生成引擎
"""
import logging
from typing import Optional, List, Dict
from pathlib import Path
import torch
from PIL import Image
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class SDGenerator:
    """Stable Diffusion + LCM 图像生成器"""

    def __init__(
        self,
        model_id: str = "runwayml/stable-diffusion-v1-5",
        lcm_lora_id: str = "latent-consistency/lcm-lora-sdv1-5",
        device: str = "cuda",
        dtype: str = "float16",
    ):
        """
        初始化生成器
        
        Args:
            model_id: 基础模型 ID
            lcm_lora_id: LCM LoRA 模型 ID (用于加速)
            device: 计算设备 ("cuda" 或 "cpu")
            dtype: 数据类型 ("float16" 或 "float32")
        """
        self.model_id = model_id
        self.lcm_lora_id = lcm_lora_id
        self.device = device
        self.dtype = torch.float16 if dtype == "float16" else torch.float32
        self.pipeline = None
        self.is_ready = False
        self._init_pipeline()

    def _init_pipeline(self):
        """初始化 Stable Diffusion 管道"""
        try:
            from diffusers import StableDiffusionPipeline, LCMScheduler
            
            logger.info(f"正在加载模型: {self.model_id}")
            logger.info(f"使用设备: CPU 模式（较慢但稳定）")
            
            # 加载基础管道（CPU模式）
            self.pipeline = StableDiffusionPipeline.from_pretrained(
                self.model_id,
                torch_dtype=torch.float32,  # CPU 必须用 float32
                safety_checker=None,  # 禁用安全检查以加速
                low_cpu_mem_usage=True,  # 降低内存使用
            )
            
            # 加载 LCM LoRA 用于加速
            try:
                logger.info(f"正在加载 LCM LoRA: {self.lcm_lora_id}")
                self.pipeline.load_lora_weights(self.lcm_lora_id)
                self.pipeline.scheduler = LCMScheduler.from_config(
                    self.pipeline.scheduler.config
                )
                logger.info("LCM LoRA 加载成功")
            except Exception as e:
                logger.warning(f"LCM LoRA 加载失败，将使用默认调度器: {e}")
            
            # 移动到 CPU
            self.pipeline.to("cpu")
            
            # CPU 模式不需要这些优化
            logger.info("生成管道初始化成功 (CPU 模式)")
            self.is_ready = True
            
        except Exception as e:
            logger.error(f"管道初始化失败: {e}")
            self.is_ready = False
            logger.warning("将在离线模式下运行，仅生成占位符图像")
    def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 512,
        height: int = 512,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 8,
        seed: Optional[int] = None,
        output_path: Optional[Path] = None,
    ) -> Image.Image:
        """
        生成单张图像
        
        Args:
            prompt: 正面提示词
            negative_prompt: 反面提示词
            width: 图像宽度
            height: 图像高度
            guidance_scale: 引导强度
            num_inference_steps: 推理步数
            seed: 随机种子
            output_path: 输出路径（可选）
            
        Returns:
            生成的 PIL Image
        """
        if not self.is_ready:
            logger.warning("生成管道未就绪，生成占位符图像")
            return self._generate_placeholder(width, height)
        
        try:
            # 设置随机种子
            if seed is None:
                seed = int(torch.randint(0, 2**32 - 1, (1,)).item())
            
            generator = torch.Generator(device=self.device)
            generator.manual_seed(seed)
            
            logger.info(f"生成图像: {prompt[:50]}... (seed: {seed})")
            
            # 生成图像
            with torch.no_grad():
                output = self.pipeline(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    height=height,
                    width=width,
                    guidance_scale=guidance_scale,
                    num_inference_steps=num_inference_steps,
                    generator=generator,
                )
            
            image = output.images[0]
            
            # 保存图像
            if output_path:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                image.save(output_path, "PNG")
                logger.info(f"图像已保存: {output_path}")
            
            return image
            
        except Exception as e:
            logger.error(f"生成失败: {e}")
            return self._generate_placeholder(width, height)

    def generate_batch(
        self,
        prompts: List[str],
        **kwargs
    ) -> List[Image.Image]:
        """
        批量生成图像
        
        Args:
            prompts: 提示词列表
            **kwargs: 传递给 generate 的其他参数
            
        Returns:
            生成的图像列表
        """
        images = []
        for i, prompt in enumerate(prompts):
            logger.info(f"生成第 {i + 1}/{len(prompts)} 张图像")
            image = self.generate(prompt, **kwargs)
            images.append(image)
        
        return images

    def _generate_placeholder(self, width: int, height: int) -> Image.Image:
        """生成占位符图像 (用于离线测试)"""
        logger.warning(f"生成占位符图像: {width}x{height}")
        
        # 创建一个简单的渐变占位符
        img_array = np.random.randint(0, 255, (height, width, 3), dtype=np.uint8)
        return Image.fromarray(img_array, "RGB")

    def generate_character_sprite_4way(
        self,
        character_description: str,
        output_dir: Path,
        seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Image.Image]:
        """
        生成四向角色精灵（北东南西）
        
        Args:
            character_description: 角色描述
            output_dir: 输出目录
            seed: 随机种子
            **kwargs: 其他生成参数
            
        Returns:
            包含四个方向图像的字典
        """
        directions = {
            "north": f"{character_description}, facing north, front view",
            "east": f"{character_description}, facing east, right side view",
            "south": f"{character_description}, facing south, back view",
            "west": f"{character_description}, facing west, left side view",
        }
        
        results = {}
        base_seed = seed if seed is not None else int(torch.randint(0, 2**32 - 1, (1,)).item())
        
        for direction, prompt in directions.items():
            # 为每个方向使用基础种子 + 偏移
            direction_seed = base_seed + (ord(direction[0]) % 256)
            
            image = self.generate(
                prompt=prompt,
                seed=direction_seed,
                output_path=output_dir / f"character_{direction}.png",
                **kwargs
            )
            results[direction] = image
        
        return results

    def generate_character_animations(
        self,
        character_description: str,
        animations: List[str],  # e.g., ["idle", "walk", "attack"]
        num_frames: int = 4,
        output_dir: Path = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> Dict[str, List[Image.Image]]:
        """
        生成角色动画序列
        
        Args:
            character_description: 角色描述
            animations: 动画类型列表
            num_frames: 每个动画的帧数
            output_dir: 输出目录
            seed: 随机种子
            **kwargs: 其他生成参数
            
        Returns:
            包含所有动画的图像列表字典
        """
        results = {}
        base_seed = seed if seed is not None else int(torch.randint(0, 2**32 - 1, (1,)).item())
        
        for anim_idx, animation in enumerate(animations):
            animation_frames = []
            
            for frame_idx in range(num_frames):
                frame_seed = base_seed + anim_idx * 256 + frame_idx
                
                prompt = f"{character_description}, {animation} animation frame {frame_idx + 1}/{num_frames}"
                
                image = self.generate(
                    prompt=prompt,
                    seed=frame_seed,
                    output_path=output_dir / f"character_{animation}_frame_{frame_idx:02d}.png" if output_dir else None,
                    **kwargs
                )
                animation_frames.append(image)
            
            results[animation] = animation_frames
        
        return results


def create_generator(
    model_id: str = "runwayml/stable-diffusion-v1-5",
    lcm_lora_id: str = "latent-consistency/lcm-lora-sdv1-5",
    device: str = "cuda",
    dtype: str = "float16",
) -> SDGenerator:
    """便捷工厂函数"""
    return SDGenerator(
        model_id=model_id,
        lcm_lora_id=lcm_lora_id,
        device=device,
        dtype=dtype,
    )
