"""
风格缓存管理模块 - 借鉴CDN缓存理念
"""
import hashlib
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import shutil

logger = logging.getLogger(__name__)


def generate_style_cache_key(style_config: dict) -> str:
    """
    生成风格缓存键
    
    计算规则:
    1. 提取核心风格参数
    2. 标准化参数值
    3. 序列化为JSON字符串
    4. 计算SHA256哈希值
    5. 取前16位作为缓存键
    
    Args:
        style_config: 风格配置字典
        
    Returns:
        缓存键字符串，格式: style_{hash16}
    """
    # 提取核心参数 (影响风格的关键字段)
    core_params = {
        'art_style': style_config.get('美术风格', style_config.get('style', 'pixel_art')),
        'color_tone': style_config.get('色彩主调', style_config.get('color_tone', 'default')),
        'seed': style_config.get('固定种子', style_config.get('seed', -1)),
        'pixel_size': style_config.get('像素尺寸', style_config.get('pixel_size', 'default')),
        'line_weight': style_config.get('线条粗细', style_config.get('line_weight', 'medium')),
        'saturation': style_config.get('饱和度', style_config.get('saturation', 50)),
    }
    
    # 标准化和排序
    normalized = {
        k: str(v).lower().strip() 
        for k, v in sorted(core_params.items())
    }
    
    # 序列化
    json_str = json.dumps(normalized, sort_keys=True, ensure_ascii=False)
    
    # 计算哈希
    hash_obj = hashlib.sha256(json_str.encode('utf-8'))
    full_hash = hash_obj.hexdigest()
    
    # 生成缓存键
    cache_key = f"style_{full_hash[:16]}"
    
    return cache_key


class StyleCacheManager:
    """
    风格缓存管理器
    
    实现三级缓存机制:
    - L1: 本地缓存 (最快, <100ms)
    - L2: Kodo对象存储 (快, <2s)  
    - L3: CDN分发 (快, <1s, 全球加速)
    """
    
    def __init__(self, cache_dir: Path, kodo_client=None):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 本地缓存目录
            kodo_client: 七牛云Kodo客户端(可选)
        """
        self.cache_dir = Path(cache_dir)
        self.styles_dir = self.cache_dir / "styles"
        self.styles_dir.mkdir(parents=True, exist_ok=True)
        self.kodo_client = kodo_client
        
        logger.info(f"风格缓存管理器初始化完成: {self.cache_dir}")
    
    def check_cache(
        self, 
        style_config: dict, 
        project_id: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Dict]]:
        """
        检查风格缓存 (三级缓存)
        
        Args:
            style_config: 风格配置
            project_id: 项目ID (用于L2/L3查询)
            
        Returns:
            (is_hit, cache_level, style_data)
            cache_level: 'L1_local' | 'L2_kodo' | 'L3_cdn' | 'miss'
        """
        cache_key = generate_style_cache_key(style_config)
        
        # L1: 本地缓存检查
        local_hit, style_data = self._check_local_cache(cache_key)
        if local_hit:
            logger.info(f"✓ L1缓存命中: {cache_key}")
            return True, 'L1_local', style_data
        
        # L2: Kodo存储检查 (如果配置了Kodo客户端)
        if self.kodo_client and project_id:
            kodo_hit, style_data = self._check_kodo_cache(cache_key, project_id)
            if kodo_hit:
                logger.info(f"✓ L2缓存命中: {cache_key}")
                # 回填到L1
                self._save_local_cache(cache_key, style_data)
                return True, 'L2_kodo', style_data
        
        # L3: CDN (通过Kodo实现,本质是L2加速)
        # CDN主要用于素材分发加速,风格模板通过L2处理
        
        # 未命中
        logger.info(f"✗ 缓存未命中: {cache_key}")
        return False, 'miss', None
    
    def _check_local_cache(self, cache_key: str) -> Tuple[bool, Optional[Dict]]:
        """检查本地缓存"""
        style_path = self.styles_dir / cache_key
        metadata_file = style_path / "metadata.json"
        
        if not metadata_file.exists():
            return False, None
        
        try:
            # 检查TTL
            with open(metadata_file, 'r', encoding='utf-8') as f:
                style_data = json.load(f)
            
            # 检查是否过期
            if self._is_expired(style_data):
                logger.info(f"缓存已过期: {cache_key}")
                return False, None
            
            return True, style_data
            
        except Exception as e:
            logger.error(f"读取本地缓存失败: {e}")
            return False, None
    
    def _check_kodo_cache(
        self, 
        cache_key: str, 
        project_id: str
    ) -> Tuple[bool, Optional[Dict]]:
        """检查Kodo存储缓存"""
        if not self.kodo_client:
            return False, None
        
        try:
            style_data = self.kodo_client.download_style_template(cache_key, project_id)
            if style_data:
                return True, style_data
            return False, None
        except Exception as e:
            logger.error(f"Kodo缓存查询失败: {e}")
            return False, None
    
    def save_style(
        self,
        cache_key: str,
        style_data: Dict,
        project_id: Optional[str] = None,
        upload_to_kodo: bool = True
    ) -> bool:
        """
        保存风格到缓存
        
        Args:
            cache_key: 缓存键
            style_data: 风格数据
            project_id: 项目ID
            upload_to_kodo: 是否上传到Kodo
            
        Returns:
            是否成功
        """
        # 添加时间戳
        style_data['cached_at'] = datetime.now().isoformat()
        style_data['cache_key'] = cache_key
        
        # L1: 保存到本地
        if not self._save_local_cache(cache_key, style_data):
            return False
        
        # L2: 上传到Kodo (如果配置)
        if upload_to_kodo and self.kodo_client and project_id:
            try:
                self.kodo_client.upload_style_template(
                    cache_key, 
                    project_id, 
                    style_data
                )
                logger.info(f"风格已上传到Kodo: {cache_key}")
            except Exception as e:
                logger.warning(f"Kodo上传失败(不影响本地缓存): {e}")
        
        return True
    
    def _save_local_cache(self, cache_key: str, style_data: Dict) -> bool:
        """保存到本地缓存"""
        try:
            style_path = self.styles_dir / cache_key
            style_path.mkdir(parents=True, exist_ok=True)
            
            metadata_file = style_path / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(style_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"风格已缓存到本地: {cache_key}")
            return True
            
        except Exception as e:
            logger.error(f"本地缓存保存失败: {e}")
            return False
    
    def _is_expired(self, style_data: Dict) -> bool:
        """检查缓存是否过期"""
        try:
            ttl_days = style_data.get('ttl_days', 30)
            cached_at = datetime.fromisoformat(style_data['cached_at'])
            expiry_date = cached_at + timedelta(days=ttl_days)
            
            return datetime.now() > expiry_date
            
        except Exception as e:
            logger.warning(f"TTL检查失败,默认未过期: {e}")
            return False
    
    def clear_cache(self, cache_key: Optional[str] = None):
        """
        清理缓存
        
        Args:
            cache_key: 指定缓存键(None表示清理全部)
        """
        if cache_key:
            style_path = self.styles_dir / cache_key
            if style_path.exists():
                shutil.rmtree(style_path)
                logger.info(f"已清理缓存: {cache_key}")
        else:
            shutil.rmtree(self.styles_dir)
            self.styles_dir.mkdir(parents=True, exist_ok=True)
            logger.info("已清理所有缓存")
    
    def get_cache_stats(self) -> Dict:
        """获取缓存统计信息"""
        styles = list(self.styles_dir.iterdir())
        total_size = sum(
            sum(f.stat().st_size for f in style_dir.rglob('*') if f.is_file())
            for style_dir in styles
        )
        
        return {
            'total_styles': len(styles),
            'total_size_mb': round(total_size / 1024 / 1024, 2),
            'cache_dir': str(self.cache_dir)
        }
    
    def calculate_hit_rate_prediction(self, style_config: dict) -> Tuple[float, str]:
        """
        预测配置的命中率
        
        Args:
            style_config: 风格配置
            
        Returns:
            (预测命中率, 建议信息)
        """
        # 计算填写的参数数量
        filled_params = sum(
            1 for v in style_config.values() 
            if v and str(v).strip() and v != '___待填___'
        )
        
        # 根据参数数量预测命中率
        if filled_params <= 2:
            hit_rate = 0.25
            suggestion = "建议至少填写5项参数以提高命中率"
        elif filled_params <= 4:
            hit_rate = 0.40
            suggestion = "建议补充种子和色彩信息"
        elif filled_params <= 6:
            hit_rate = 0.60
            suggestion = "配置较好,建议添加提示词模板"
        elif filled_params <= 8:
            hit_rate = 0.80
            suggestion = "配置优秀,命中率高"
        else:
            hit_rate = 0.95
            suggestion = "完美配置,极高命中率"
        
        return hit_rate, suggestion


# 测试代码
if __name__ == "__main__":
    # 测试缓存键生成
    style_config = {
        "美术风格": "pixel_art",
        "色彩主调": "warm_tones",
        "固定种子": 42,
        "像素尺寸": "16px"
    }
    
    cache_key = generate_style_cache_key(style_config)
    print(f"缓存键: {cache_key}")
    
    # 测试缓存管理器
    manager = StyleCacheManager(cache_dir=Path("cache"))
    
    # 测试命中率预测
    hit_rate, suggestion = manager.calculate_hit_rate_prediction(style_config)
    print(f"预测命中率: {hit_rate*100:.1f}%")
    print(f"建议: {suggestion}")
