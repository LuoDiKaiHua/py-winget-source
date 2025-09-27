# py-winget-source

一个可扩展的 Python 脚本，用于读取 manifest 配置并从不同站点获取软件包的最新 release 信息。

## 功能特性

- 📦 支持从 manifest.yml 文件读取包配置
- 🔄 自动获取 GitHub 仓库的最新 release 信息
- 🏗️ 可扩展的架构设计，支持添加更多站点
- ⚡ 异步并发处理，提高效率
- 🎯 智能选择下载链接（优先 .exe 文件）

## 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -r requirements.txt
```

## 使用方法

1. 配置 `manifest.yml` 文件：

```yaml
packages:
  - name: usql
    id: xo.usql
    url: https://github.com/xo/usql
  - name: another-package
    id: com.example.package
    url: https://github.com/example/repo
```

2. 运行脚本：

```bash
python main.py
```

## 扩展支持其他站点

### 1. 创建新的包管理器

参考 `examples/gitlab_manager.py` 创建新的包管理器：

```python
from package_managers.base import PackageManager, ReleaseInfo

class CustomPackageManager(PackageManager):
    def __init__(self):
        super().__init__("https://example.com")
    
    def can_handle(self, url: str) -> bool:
        # 判断是否能处理该 URL
        return "example.com" in url
    
    def extract_repo_info(self, url: str) -> tuple[str, str]:
        # 从 URL 中提取仓库信息
        pass
    
    async def get_latest_release(self, url: str) -> Optional[ReleaseInfo]:
        # 获取最新 release 信息
        pass
```

### 2. 注册新的包管理器

在 `main.py` 中注册：

```python
from examples.custom_manager import CustomPackageManager

# 在创建 registry 后添加
registry.register(CustomPackageManager())
```

## 项目结构

```
py-winget-source/
├── main.py                 # 主程序入口
├── manifest_parser.py      # Manifest 文件解析器
├── manifest.yml           # 包配置文件
├── package_managers/      # 包管理器模块
│   ├── __init__.py
│   ├── base.py           # 基础抽象类
│   ├── github.py         # GitHub 包管理器
│   └── registry.py       # 包管理器注册表
├── examples/             # 扩展示例
│   ├── __init__.py
│   └── gitlab_manager.py # GitLab 包管理器示例
└── pyproject.toml        # 项目配置
```

## 架构设计

### 核心组件

1. **PackageManager** - 抽象基类，定义包管理器的接口
2. **PackageManagerRegistry** - 注册表，管理所有可用的包管理器
3. **ManifestParser** - 解析 manifest.yml 配置文件
4. **ReleaseInfo** - 统一的数据结构，存储 release 信息

### 扩展性

- 通过继承 `PackageManager` 类可以轻松添加新站点支持
- 使用注册表模式自动选择合适的包管理器
- 统一的 `ReleaseInfo` 数据结构确保一致性

## 支持的站点

- ✅ GitHub (github.com)
- 🔄 GitLab (gitlab.com) - 示例实现
- ➕ 更多站点可通过扩展添加

## 开发

### 运行测试

```bash
python main.py
```

### 代码检查

```bash
# 使用项目配置的 linter
python -m flake8 .
```

## 许可证

MIT License
