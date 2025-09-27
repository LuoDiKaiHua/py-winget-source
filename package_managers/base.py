"""包管理器基础抽象类"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from urllib.parse import ParseResult, urlparse


@dataclass
class ReleaseInfo:
    """Release 信息数据类"""

    version: str
    tag_name: str
    download_url: str
    published_at: str
    release_notes: Optional[str] = None


class PackageManager(ABC):
    """包管理器抽象基类"""

    def __init__(self, base_url: str):
        self.base_url = base_url

    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """判断是否能处理该 URL"""
        pass

    @abstractmethod
    async def get_latest_release(self, url: str, include_prerelease: bool = False, pattern: str = "") -> Optional[ReleaseInfo]:
        """获取最新 release 信息
        
        Args:
            url: 仓库 URL
            include_prerelease: 是否包含预发布版本
            pattern: 文件名匹配模式（正则表达式）
        """
        pass

    @abstractmethod
    def extract_repo_info(self, url: str) -> tuple[str, str]:
        """从 URL 中提取仓库信息 (owner, repo)"""
        pass

    def _parse_url(self, url: str) -> ParseResult:
        """解析 URL"""
        return urlparse(url)
