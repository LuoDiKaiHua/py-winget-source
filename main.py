"""主程序 - 读取 manifest 配置并获取最新 release 信息"""

import asyncio
import sys

from manifest_parser import ManifestParser, PackageInfo
from package_managers import PackageManagerRegistry


async def process_package(package: PackageInfo, registry: PackageManagerRegistry) -> None:
    """处理单个包的信息获取"""
    print(f"\n处理包: {package.name} ({package.id})")
    print(f"URL: {package.url}")
    if package.pattern:
        print(f"匹配模式: {package.pattern}")

    release_info = await registry.get_latest_release(
        package.url, 
        include_prerelease=package.include_prerelease,
        pattern=package.pattern
    )

    if release_info:
        print(f"✅ 最新版本: {release_info.version}")
        print(f"   标签: {release_info.tag_name}")
        print(f"   下载链接: {release_info.download_url}")
        if release_info.published_at:
            print(f"   发布时间: {release_info.published_at}")
        if release_info.release_notes:
            # 只显示前 100 个字符的发布说明
            notes_preview = release_info.release_notes[:100]
            if len(release_info.release_notes) > 100:
                notes_preview += "..."
            print(f"   发布说明: {notes_preview}")
    else:
        print("❌ 无法获取 release 信息")


async def main():
    """主函数"""
    print("🚀 开始处理 manifest 配置...")

    # 解析 manifest 文件
    parser = ManifestParser()
    packages = parser.parse()

    if not packages:
        print("❌ 没有找到任何包配置")
        return

    print(f"📦 找到 {len(packages)} 个包配置")

    # 创建包管理器注册表
    registry = PackageManagerRegistry()

    # 并发处理所有包
    tasks = [process_package(package, registry) for package in packages]
    await asyncio.gather(*tasks)

    print("\n✨ 处理完成!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        sys.exit(1)
