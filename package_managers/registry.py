"""包管理器注册表"""

from typing import List, Optional

from .base import PackageManager, ReleaseInfo
from .github import GitHubPackageManager


class PackageManagerRegistry:
    """包管理器注册表 - 管理所有可用的包管理器"""
    
    def __init__(self):
        self._managers: List[PackageManager] = []
        self._register_default_managers()
    
    def _register_default_managers(self):
        """注册默认的包管理器"""
        # 可以传入 GitHub token 以提高 API 限制
        github_token = None  # 可以从环境变量获取或配置文件读取
        self.register(GitHubPackageManager(token=github_token))
    
    def register(self, manager: PackageManager):
        """注册新的包管理器"""
        self._managers.append(manager)
    
    def get_manager(self, url: str) -> Optional[PackageManager]:
        """根据 URL 获取合适的包管理器"""
        for manager in self._managers:
            if manager.can_handle(url):
                return manager
        return None
    
    async def get_latest_release(self, url: str, include_prerelease: bool = False, pattern: str = "") -> Optional[ReleaseInfo]:
        """获取指定 URL 的最新 release
        
        Args:
            url: 仓库 URL
            include_prerelease: 是否包含预发布版本
            pattern: 文件名匹配模式（正则表达式）
        """
        manager = self.get_manager(url)
        if not manager:
            print(f"没有找到支持该 URL 的包管理器: {url}")
            return None
        
        return await manager.get_latest_release(url, include_prerelease=include_prerelease, pattern=pattern)
