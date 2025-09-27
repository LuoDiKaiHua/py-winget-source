"""Manifest 解析器"""

from dataclasses import dataclass
from typing import List

import yaml


@dataclass
class PackageInfo:
    """包信息数据类"""

    name: str
    id: str
    url: str
    include_prerelease: bool = False
    pattern: str = ""


class ManifestParser:
    """Manifest 文件解析器"""

    def __init__(self, manifest_path: str = "manifest.yml"):
        self.manifest_path = manifest_path

    def parse(self) -> List[PackageInfo]:
        """解析 manifest 文件"""
        try:
            with open(self.manifest_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)

            packages = []
            if "packages" in data:
                # 处理 YAML 列表格式
                for package_data in data["packages"]:
                    if isinstance(package_data, dict):
                        # 字典格式: {name: ..., id: ..., url: ..., pattern: ..., include_prerelease: ...}
                        package = PackageInfo(
                            name=package_data.get("name", ""),
                            id=package_data.get("id", ""),
                            url=package_data.get("url", ""),
                            include_prerelease=package_data.get("include_prerelease", False),
                            pattern=package_data.get("pattern", ""),
                        )
                    else:
                        # 列表格式: [name, id, url]
                        if len(package_data) >= 3:
                            package = PackageInfo(name=package_data[0], id=package_data[1], url=package_data[2])
                        else:
                            print(f"警告: 包信息不完整: {package_data}")
                            continue

                    # 只添加有效的包（必须有 URL）
                    if package.url:
                        packages.append(package)
                    else:
                        print(f"警告: 跳过没有 URL 的包: {package.name}")

            return packages

        except FileNotFoundError:
            print(f"错误: 找不到 manifest 文件: {self.manifest_path}")
            return []
        except yaml.YAMLError as e:
            print(f"错误: 解析 YAML 文件失败: {e}")
            return []
        except Exception as e:
            print(f"错误: 解析 manifest 文件时出错: {e}")
            return []
