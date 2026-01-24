"""
缓存管理器 - 管理分析结果的缓存
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any

from utils.logger import get_logger

logger = get_logger()


class CacheManager:
    """缓存管理器 - 支持断点续传和结果复用"""
    
    def __init__(self, cache_dir: str, enabled: bool = True):
        """
        初始化缓存管理器
        
        Args:
            cache_dir: 缓存目录
            enabled: 是否启用缓存
        """
        self.cache_dir = cache_dir
        self.enabled = enabled
        
        if enabled:
            os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, project: str, commit_hash: str, phase: str) -> str:
        """生成缓存键"""
        return f"{project}_{commit_hash}_{phase}"
    
    def _get_cache_path(self, cache_key: str) -> str:
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def has_cache(self, project: str, commit_hash: str, phase: str) -> bool:
        """检查是否有缓存"""
        if not self.enabled:
            return False
        
        cache_key = self._get_cache_key(project, commit_hash, phase)
        cache_path = self._get_cache_path(cache_key)
        return os.path.exists(cache_path)
    
    def get_cache(self, project: str, commit_hash: str, phase: str) -> Optional[Dict[str, Any]]:
        """获取缓存数据"""
        if not self.enabled:
            return None
        
        cache_key = self._get_cache_key(project, commit_hash, phase)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.debug(f"从缓存加载: {cache_key}")
                return data
        except Exception as e:
            logger.warning(f"读取缓存失败 {cache_key}: {e}")
            return None
    
    def set_cache(self, project: str, commit_hash: str, phase: str, data: Dict[str, Any]):
        """设置缓存数据"""
        if not self.enabled:
            return
        
        cache_key = self._get_cache_key(project, commit_hash, phase)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            # 添加缓存元数据
            cache_data = {
                'cache_key': cache_key,
                'cached_at': datetime.now().isoformat(),
                'project': project,
                'commit_hash': commit_hash,
                'phase': phase,
                'data': data
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"缓存已保存: {cache_key}")
        except Exception as e:
            logger.warning(f"保存缓存失败 {cache_key}: {e}")
    
    def clear_cache(self, project: str = None, commit_hash: str = None):
        """清除缓存"""
        if not self.enabled or not os.path.exists(self.cache_dir):
            return
        
        count = 0
        for filename in os.listdir(self.cache_dir):
            if not filename.endswith('.json'):
                continue
            
            should_delete = True
            if project and not filename.startswith(f"{project}_"):
                should_delete = False
            if commit_hash and commit_hash not in filename:
                should_delete = False
            
            if should_delete:
                try:
                    os.remove(os.path.join(self.cache_dir, filename))
                    count += 1
                except Exception as e:
                    logger.warning(f"删除缓存失败 {filename}: {e}")
        
        logger.info(f"已清除 {count} 个缓存文件")
    
    def get_cached_commits(self, project: str, phase: str) -> set:
        """获取已缓存的commit列表"""
        if not self.enabled or not os.path.exists(self.cache_dir):
            return set()
        
        cached = set()
        prefix = f"{project}_"
        suffix = f"_{phase}.json"
        
        for filename in os.listdir(self.cache_dir):
            if filename.startswith(prefix) and filename.endswith(suffix):
                # 提取commit hash
                commit_hash = filename[len(prefix):-len(suffix)]
                cached.add(commit_hash)
        
        return cached
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        if not self.enabled or not os.path.exists(self.cache_dir):
            return {'enabled': False, 'count': 0, 'size_mb': 0}
        
        count = 0
        total_size = 0
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                count += 1
                filepath = os.path.join(self.cache_dir, filename)
                total_size += os.path.getsize(filepath)
        
        return {
            'enabled': True,
            'count': count,
            'size_mb': round(total_size / (1024 * 1024), 2)
        }
