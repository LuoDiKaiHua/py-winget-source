"""GitHub 包管理器实现"""

import os
import re
from typing import Optional

import aiohttp

from .base import PackageManager, ReleaseInfo


class GitHubPackageManager(PackageManager):
    """GitHub 包管理器 - 使用 GitHub API v4 (REST API)"""

    def __init__(self, token: Optional[str] = None):
        super().__init__("https://github.com")
        self.api_base = "https://api.github.com"
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "py-winget-source/1.0"}
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"

    def can_handle(self, url: str) -> bool:
        """判断是否为 GitHub URL"""
        parsed = self._parse_url(url)
        return parsed.netloc.lower() in ["github.com", "www.github.com"]

    def extract_repo_info(self, url: str) -> tuple[str, str]:
        """从 GitHub URL 中提取 owner 和 repo"""
        # 支持多种 GitHub URL 格式
        patterns = [
            r"github\.com/([^/]+)/([^/]+?)(?:\.git)?/?(?:\?.*)?$",  # https://github.com/owner/repo
            r"github\.com/([^/]+)/([^/]+?)(?:\.git)?/(?:tree|blob|releases|actions|issues|pull)/",  # 各种子页面
            r"github\.com/([^/]+)/([^/]+?)(?:\.git)?/archive/",  # 下载链接
        ]

        for pattern in patterns:
            match = re.search(pattern, url.lower())
            if match:
                owner, repo = match.group(1), match.group(2)
                # 清理仓库名称，移除可能的后缀
                if repo.endswith(".git"):
                    repo = repo[:-4]
                return owner, repo

        raise ValueError(f"无法从 URL 中提取仓库信息: {url}")

    async def get_latest_release(
        self, url: str, include_prerelease: bool = False, pattern: str = ""
    ) -> Optional[ReleaseInfo]:
        """获取 GitHub 仓库的最新 release

        Args:
            url: GitHub 仓库 URL
            include_prerelease: 是否包含预发布版本
            pattern: 文件名匹配模式（正则表达式）
        """
        try:
            owner, repo = self.extract_repo_info(url)

            # 首先尝试获取最新的稳定版本或预发布版本
            if include_prerelease:
                return await self._get_latest_release_including_prerelease(owner, repo, pattern)
            else:
                return await self._get_latest_stable_release(owner, repo, pattern)

        except Exception as e:
            print(f"获取 GitHub release 时出错: {e}")
            return None

    async def _get_latest_stable_release(self, owner: str, repo: str, pattern: str = "") -> Optional[ReleaseInfo]:
        """获取最新的稳定版本 release"""
        api_url = f"{self.api_base}/repos/{owner}/{repo}/releases/latest"

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=self.headers) as response:
                if response.status == 404:
                    print(f"仓库 {owner}/{repo} 没有发布任何 release")
                    return None
                elif response.status == 403:
                    print(f"API 限制或权限问题: {response.status}")
                    return None
                elif response.status != 200:
                    print(f"获取 release 失败: HTTP {response.status}")
                    return None

                data = await response.json()
                return self._parse_release_data(data, pattern)

    async def _get_latest_release_including_prerelease(
        self, owner: str, repo: str, pattern: str = ""
    ) -> Optional[ReleaseInfo]:
        """获取最新版本（包括预发布版本）"""
        api_url = f"{self.api_base}/repos/{owner}/{repo}/releases"

        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, headers=self.headers, params={"per_page": 10}) as response:
                if response.status == 404:
                    print(f"仓库 {owner}/{repo} 没有发布任何 release")
                    return None
                elif response.status == 403:
                    print(f"API 限制或权限问题: {response.status}")
                    return None
                elif response.status != 200:
                    print(f"获取 releases 失败: HTTP {response.status}")
                    return None

                releases = await response.json()
                if not releases:
                    print(f"仓库 {owner}/{repo} 没有任何 release")
                    return None

                # 返回最新的 release（第一个）
                return self._parse_release_data(releases[0], pattern)

    def _parse_release_data(self, data: dict, pattern: str = "") -> ReleaseInfo:
        """解析 GitHub API 返回的 release 数据，根据 pattern 选择资源文件"""
        download_url = None

        if data.get("assets") and pattern:
            # 使用 pattern 匹配选择资源文件
            download_url = self._select_asset_by_pattern(data["assets"], pattern)

        # 如果没有 pattern 或没有匹配的文件，返回空的下载链接
        return ReleaseInfo(
            version=data["tag_name"],
            tag_name=data["tag_name"],
            download_url=download_url or "",
            published_at=data.get("published_at", ""),
            release_notes=data.get("body"),
        )

    def _select_asset_by_pattern(self, assets: list, pattern: str) -> str:
        """根据正则表达式 pattern 选择匹配的资源文件"""
        import re

        if not pattern:
            return ""

        try:
            # 编译正则表达式
            regex = re.compile(pattern, re.IGNORECASE)

            # 找到所有匹配的资源文件
            matching_assets = []
            for asset in assets:
                if regex.search(asset["name"]):
                    matching_assets.append(asset)

            if not matching_assets:
                print(f"没有找到匹配 pattern '{pattern}' 的资源文件")
                return ""

            # 如果有多个匹配的文件，选择下载量最多的
            # 如果下载量相同，选择文件名最短的
            best_asset = max(matching_assets, key=lambda x: (x.get("download_count", 0), -len(x["name"])))

            print(f"找到 {len(matching_assets)} 个匹配的文件，选择: {best_asset['name']}")
            return best_asset["browser_download_url"]

        except re.error as e:
            print(f"正则表达式 pattern '{pattern}' 有误: {e}")
            return ""
        except Exception as e:
            print(f"处理 pattern 时出错: {e}")
            return ""

    async def get_repository_info(self, url: str) -> Optional[dict]:
        """获取仓库的基本信息"""
        try:
            owner, repo = self.extract_repo_info(url)
            api_url = f"{self.api_base}/repos/{owner}/{repo}"

            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        print(f"获取仓库信息失败: HTTP {response.status}")
                        return None

        except Exception as e:
            print(f"获取仓库信息时出错: {e}")
            return None

    async def check_rate_limit(self) -> dict:
        """检查 API 限制状态"""
        api_url = f"{self.api_base}/rate_limit"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"HTTP {response.status}"}

        except Exception as e:
            return {"error": str(e)}
