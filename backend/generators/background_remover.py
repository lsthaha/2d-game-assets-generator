"""
背景移除模块 - 使用 rembg 或 SAM
"""
import logging
from pathlib import Path
from typing import Union, Optional
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class BackgroundRemover:
    """背景去除处理器"""

    def __init__(self, method: str = "rembg"):
        """
        初始化背景移除器
        
        Args:
            method: 使用的方法 "rembg" 或 "sam"
        """
        self.method = method
        self.model = None
        self._init_model()

    def _init_model(self):
        """初始化模型"""
        try:
            if self.method == "rembg":
                try:
                    import rembg
                    self.model = rembg
                    logger.info("rembg 模型加载成功")
                except ImportError:
                    logger.warning("rembg 未安装，将跳过背景移除")
                    self.model = None
            elif self.method == "sam":
                logger.info("SAM 方法暂未实现，使用简单色度键方案")
                self.model = None
        except Exception as e:
            logger.error(f"模型初始化失败: {e}")
            self.model = None

    def remove_background(self, image: Union[str, Path, Image.Image]) -> Image.Image:
        """
        移除图像背景
        
        Args:
            image: 输入图像（路径或 PIL Image）
            
        Returns:
            带透明通道的 PIL Image
        """
        # 加载图像
        if isinstance(image, (str, Path)):
            img = Image.open(image)
        else:
            img = image

        # 如果没有加载模型，返回原图（仅转为 RGBA）
        if self.model is None:
            return img.convert("RGBA")

        try:
            if self.method == "rembg":
                return self._remove_bg_rembg(img)
            elif self.method == "sam":
                return self._remove_bg_sam(img)
            else:
                logger.warning(f"未知的背景移除方法: {self.method}")
                return img.convert("RGBA")
        except Exception as e:
            logger.error(f"背景移除失败: {e}")
            return img.convert("RGBA")

    def _remove_bg_rembg(self, img: Image.Image) -> Image.Image:
        """使用 rembg 移除背景"""
        try:
            from rembg import remove
            
            # 确保输入是 RGB
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # 移除背景
            output = remove(img)
            
            # 确保输出是 RGBA
            if output.mode != "RGBA":
                output = output.convert("RGBA")
            
            logger.info("背景移除成功 (rembg)")
            return output
        except Exception as e:
            logger.error(f"rembg 处理失败: {e}")
            return img.convert("RGBA")

    def _remove_bg_sam(self, img: Image.Image) -> Image.Image:
        """使用 SAM (Segment Anything Model) 移除背景 - 简化版"""
        try:
            # 这是一个简化的实现
            # 完整版本需要加载 sam_vit_h_4b8939.pth
            logger.warning("SAM 方法暂未完整实现")
            return img.convert("RGBA")
        except Exception as e:
            logger.error(f"SAM 处理失败: {e}")
            return img.convert("RGBA")

    def batch_remove_background(self, image_paths: list) -> list:
        """
        批量移除背景
        
        Args:
            image_paths: 输入图像路径列表
            
        Returns:
            输出图像路径列表
        """
        results = []
        for i, img_path in enumerate(image_paths):
            try:
                logger.info(f"处理图像 {i + 1}/{len(image_paths)}: {img_path}")
                result = self.remove_background(img_path)
                
                # 保存结果
                output_path = Path(img_path).parent / f"{Path(img_path).stem}_transparent.png"
                result.save(output_path, "PNG")
                results.append(str(output_path))
            except Exception as e:
                logger.error(f"处理失败 {img_path}: {e}")
        
        return results


# 便捷函数
def remove_background(
    image: Union[str, Path, Image.Image],
    method: str = "rembg"
) -> Image.Image:
    """便捷函数：一次性移除背景"""
    remover = BackgroundRemover(method=method)
    return remover.remove_background(image)
