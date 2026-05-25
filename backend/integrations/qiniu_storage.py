"""
七牛云Kodo对象存储集成模块
"""
import json
import logging
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from qiniu import Auth, put_file, BucketManager
    import qiniu.config
    QINIU_AVAILABLE = True
except ImportError:
    QINIU_AVAILABLE = False
    logger.warning("七牛云SDK未安装,Kodo功能将被禁用。安装: pip install qiniu")


class QiniuKodoClient:
    """
    七牛云Kodo对象存储客户端
    
    功能:
    - 素材上传到Kodo
    - 元数据管理
    - CDN URL生成
    - 风格模板同步
    """
    
    def __init__(
        self,
        access_key: str,
        secret_key: str,
        bucket_name: str,
        cdn_domain: Optional[str] = None,
        region: str = "z0"
    ):
        """
        初始化Kodo客户端
        
        Args:
            access_key: 七牛云AccessKey
            secret_key: 七牛云SecretKey
            bucket_name: 存储空间名称
            cdn_domain: CDN加速域名
            region: 存储区域 (z0=华东, z1=华北, z2=华南, na0=北美, as0=东南亚)
        """
        if not QINIU_AVAILABLE:
            raise ImportError("请先安装七牛云SDK: pip install qiniu")
        
        self.auth = Auth(access_key, secret_key)
        self.bucket_name = bucket_name
        self.cdn_domain = cdn_domain or f"{bucket_name}.qiniucdn.com"
        self.region = region
        self.bucket_manager = BucketManager(self.auth)
        
        logger.info(f"Kodo客户端初始化完成: bucket={bucket_name}, region={region}")
    
    def upload_asset(
        self,
        local_file_path: str,
        project_id: str,
        asset_type: str,
        asset_id: str,
        metadata: Optional[Dict] = None,
        overwrite: bool = False
    ) -> Optional[str]:
        """
        上传素材到Kodo
        
        Args:
            local_file_path: 本地文件路径
            project_id: 项目ID
            asset_type: 素材类型 (character, background, tileset, ui_icon)
            asset_id: 素材ID
            metadata: 元数据(可选)
            overwrite: 是否覆盖已有文件
            
        Returns:
            CDN URL if successful, None otherwise
        """
        try:
            # 构建Kodo路径
            file_ext = Path(local_file_path).suffix
            kodo_key = f"projects/{project_id}/assets/{asset_type}s/{asset_id}{file_ext}"
            
            # 生成上传token
            policy = {'insertOnly': 0 if overwrite else 1}  # 0=允许覆盖, 1=仅插入
            token = self.auth.upload_token(self.bucket_name, kodo_key, 3600, policy)
            
            # 上传文件
            ret, info = put_file(token, kodo_key, local_file_path)
            
            if info.status_code == 200:
                logger.info(f"✓ 素材上传成功: {kodo_key}")
                
                # 上传元数据
                if metadata:
                    metadata['kodo_key'] = kodo_key
                    metadata['uploaded_at'] = datetime.now().isoformat()
                    metadata_key = f"projects/{project_id}/assets/{asset_type}s/{asset_id}.json"
                    self._upload_json(metadata_key, metadata)
                
                # 返回CDN URL
                cdn_url = self.get_cdn_url(kodo_key)
                return cdn_url
            else:
                logger.error(f"✗ 上传失败: {info.status_code} - {info.error}")
                return None
                
        except Exception as e:
            logger.error(f"✗ Kodo上传异常: {e}")
            return None
    
    def upload_style_template(
        self,
        style_cache_key: str,
        project_id: str,
        style_data: Dict
    ) -> bool:
        """
        上传风格模板到Kodo
        
        Args:
            style_cache_key: 风格缓存键
            project_id: 项目ID
            style_data: 风格数据
            
        Returns:
            是否成功
        """
        try:
            # 添加上传时间戳
            style_data['uploaded_to_kodo_at'] = datetime.now().isoformat()
            
            # 构建Kodo路径
            style_key = f"projects/{project_id}/styles/{style_cache_key}/metadata.json"
            
            # 上传
            success = self._upload_json(style_key, style_data)
            
            if success:
                logger.info(f"✓ 风格模板上传成功: {style_cache_key}")
            
            return success
            
        except Exception as e:
            logger.error(f"✗ 风格模板上传失败: {e}")
            return False
    
    def download_style_template(
        self,
        style_cache_key: str,
        project_id: str
    ) -> Optional[Dict]:
        """
        从Kodo下载风格模板
        
        Args:
            style_cache_key: 风格缓存键
            project_id: 项目ID
            
        Returns:
            风格数据字典,失败返回None
        """
        try:
            # 构建Kodo路径
            style_key = f"projects/{project_id}/styles/{style_cache_key}/metadata.json"
            
            # 生成下载URL
            base_url = f"http://{self.cdn_domain}/{style_key}"
            private_url = self.auth.private_download_url(base_url, expires=3600)
            
            # 下载数据
            import requests
            response = requests.get(private_url, timeout=10)
            
            if response.status_code == 200:
                style_data = response.json()
                logger.info(f"✓ 风格模板下载成功: {style_cache_key}")
                return style_data
            elif response.status_code == 404:
                logger.info(f"风格模板不存在: {style_cache_key}")
                return None
            else:
                logger.error(f"✗ 下载失败: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"✗ 风格模板下载异常: {e}")
            return None
    
    def _upload_json(self, key: str, data: Dict) -> bool:
        """
        上传JSON数据到Kodo
        
        Args:
            key: Kodo对象键
            data: 数据字典
            
        Returns:
            是否成功
        """
        try:
            # 序列化JSON
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            json_bytes = json_str.encode('utf-8')
            
            # 生成上传token
            token = self.auth.upload_token(self.bucket_name, key, 3600)
            
            # 使用put_data上传
            from qiniu import put_data
            ret, info = put_data(token, key, json_bytes)
            
            if info.status_code == 200:
                return True
            else:
                logger.error(f"JSON上传失败: {info.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"JSON上传异常: {e}")
            return False
    
    def get_cdn_url(self, kodo_key: str, https: bool = True) -> str:
        """
        获取资源的CDN URL
        
        Args:
            kodo_key: Kodo对象键
            https: 是否使用HTTPS
            
        Returns:
            CDN URL
        """
        protocol = "https" if https else "http"
        return f"{protocol}://{self.cdn_domain}/{kodo_key}"
    
    def get_private_download_url(self, kodo_key: str, expires: int = 3600) -> str:
        """
        获取私有资源的下载URL(带鉴权)
        
        Args:
            kodo_key: Kodo对象键
            expires: 过期时间(秒)
            
        Returns:
            带鉴权的下载URL
        """
        base_url = self.get_cdn_url(kodo_key)
        return self.auth.private_download_url(base_url, expires=expires)
    
    def list_project_assets(
        self,
        project_id: str,
        asset_type: Optional[str] = None,
        limit: int = 100
    ) -> list:
        """
        列出项目的素材文件
        
        Args:
            project_id: 项目ID
            asset_type: 素材类型过滤(可选)
            limit: 返回数量限制
            
        Returns:
            文件列表
        """
        try:
            # 构建前缀
            if asset_type:
                prefix = f"projects/{project_id}/assets/{asset_type}s/"
            else:
                prefix = f"projects/{project_id}/assets/"
            
            # 列举文件
            ret, eof, info = self.bucket_manager.list(
                self.bucket_name,
                prefix=prefix,
                limit=limit
            )
            
            if info.status_code == 200:
                items = ret.get('items', [])
                logger.info(f"查询到 {len(items)} 个文件")
                return items
            else:
                logger.error(f"列举文件失败: {info.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"列举文件异常: {e}")
            return []
    
    def delete_asset(self, kodo_key: str) -> bool:
        """
        删除素材
        
        Args:
            kodo_key: Kodo对象键
            
        Returns:
            是否成功
        """
        try:
            ret, info = self.bucket_manager.delete(self.bucket_name, kodo_key)
            
            if info.status_code == 200:
                logger.info(f"✓ 删除成功: {kodo_key}")
                return True
            else:
                logger.error(f"✗ 删除失败: {info.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"删除异常: {e}")
            return False
    
    def get_bucket_info(self) -> Optional[Dict]:
        """
        获取存储空间信息
        
        Returns:
            存储空间信息
        """
        try:
            # 获取空间配额
            ret, info = self.bucket_manager.bucket_info(self.bucket_name)
            
            if info.status_code == 200:
                return ret
            else:
                logger.error(f"获取bucket信息失败: {info.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"获取bucket信息异常: {e}")
            return None


class MockQiniuKodoClient:
    """
    Mock Kodo客户端 (用于没有安装SDK或测试环境)
    """
    
    def __init__(self, *args, **kwargs):
        logger.warning("使用Mock Kodo客户端,功能受限")
        self.bucket_name = kwargs.get('bucket_name', 'mock-bucket')
        self.cdn_domain = kwargs.get('cdn_domain', 'mock.cdn.com')
    
    def upload_asset(self, *args, **kwargs):
        logger.info("Mock: 跳过上传")
        return f"https://{self.cdn_domain}/mock_asset.png"
    
    def upload_style_template(self, *args, **kwargs):
        logger.info("Mock: 跳过风格模板上传")
        return True
    
    def download_style_template(self, *args, **kwargs):
        logger.info("Mock: 返回空风格模板")
        return None
    
    def get_cdn_url(self, kodo_key: str, *args, **kwargs):
        return f"https://{self.cdn_domain}/{kodo_key}"


# 工厂函数
def create_kodo_client(
    access_key: Optional[str] = None,
    secret_key: Optional[str] = None,
    bucket_name: Optional[str] = None,
    **kwargs
) -> QiniuKodoClient:
    """
    创建Kodo客户端(自动判断是否可用)
    
    Returns:
        QiniuKodoClient或MockQiniuKodoClient
    """
    if not QINIU_AVAILABLE or not all([access_key, secret_key, bucket_name]):
        logger.warning("Kodo客户端不可用,使用Mock模式")
        return MockQiniuKodoClient(
            access_key=access_key,
            secret_key=secret_key,
            bucket_name=bucket_name,
            **kwargs
        )
    
    return QiniuKodoClient(
        access_key=access_key,
        secret_key=secret_key,
        bucket_name=bucket_name,
        **kwargs
    )


# 测试代码
if __name__ == "__main__":
    # 测试Mock客户端
    client = create_kodo_client()
    
    url = client.upload_asset(
        local_file_path="test.png",
        project_id="proj_test",
        asset_type="character",
        asset_id="char_001"
    )
    
    print(f"上传结果: {url}")
