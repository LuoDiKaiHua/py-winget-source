"""包管理器模块 - 支持从不同站点获取最新 release 信息"""

from .base import PackageManager, ReleaseInfo
from .github import GitHubPackageManager
from .registry import PackageManagerRegistry

__all__ = [
    "PackageManager",
    "ReleaseInfo", 
    "GitHubPackageManager",
    "PackageManagerRegistry"
]
