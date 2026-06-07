"""MCP 工具市场 / MCP Tool Marketplace.

管理 MCP Server 注册、发现、安装。
Phase 1: 内置工具注册表
Phase 2: 远程 MCP Server 连接 + Marketplace UI
"""

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class MCPServerInfo:
    """MCP Server 信息."""
    id: str
    name: str
    description: str
    version: str
    category: str  # builtin / community / enterprise
    transport: str  # stdio / http / sse
    endpoint: str = ""
    tools: list[dict] = field(default_factory=list)
    resources: list[dict] = field(default_factory=list)
    prompts: list[dict] = field(default_factory=list)
    installed: bool = False
    enabled: bool = True

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "category": self.category,
            "transport": self.transport,
            "endpoint": self.endpoint,
            "tools_count": len(self.tools),
            "tools": self.tools,
            "resources": self.resources,
            "prompts": self.prompts,
            "installed": self.installed,
            "enabled": self.enabled,
        }


class MCPMarketplace:
    """MCP 工具市场.

    注册和管理 MCP Server。
    """

    def __init__(self) -> None:
        self._servers: dict[str, MCPServerInfo] = {}
        self._init_builtin()

    def _init_builtin(self) -> None:
        """注册内置 MCP Server."""
        servers = [
            MCPServerInfo(
                id="filesystem",
                name="Filesystem",
                description="文件系统操作 — 读写文件、目录遍历、搜索",
                version="1.0.0",
                category="builtin",
                transport="stdio",
                tools=[
                    {"name": "read_file", "description": "读取文件内容"},
                    {"name": "write_file", "description": "写入文件"},
                    {"name": "list_directory", "description": "列出目录"},
                    {"name": "search_files", "description": "搜索文件"},
                    {"name": "get_file_info", "description": "获取文件信息"},
                ],
                installed=True,
            ),
            MCPServerInfo(
                id="git",
                name="Git",
                description="Git 版本控制 — clone、commit、push、diff、log",
                version="1.0.0",
                category="builtin",
                transport="stdio",
                tools=[
                    {"name": "git_clone", "description": "克隆仓库"},
                    {"name": "git_status", "description": "获取状态"},
                    {"name": "git_commit", "description": "提交更改"},
                    {"name": "git_push", "description": "推送远程"},
                    {"name": "git_diff", "description": "查看差异"},
                    {"name": "git_log", "description": "查看日志"},
                ],
                installed=True,
            ),
            MCPServerInfo(
                id="terminal",
                name="Terminal",
                description="终端命令执行 — 在沙箱中执行 Shell 命令",
                version="1.0.0",
                category="builtin",
                transport="stdio",
                tools=[
                    {"name": "run_command", "description": "执行命令"},
                    {"name": "run_script", "description": "执行脚本"},
                ],
                installed=True,
            ),
            MCPServerInfo(
                id="browser",
                name="Browser",
                description="浏览器自动化 — Playwright/Puppeteer 操作",
                version="0.1.0",
                category="builtin",
                transport="stdio",
                tools=[
                    {"name": "navigate", "description": "导航到 URL"},
                    {"name": "screenshot", "description": "截屏"},
                    {"name": "click", "description": "点击元素"},
                    {"name": "type_text", "description": "输入文本"},
                ],
                installed=True,
            ),
            MCPServerInfo(
                id="github",
                name="GitHub",
                description="GitHub API — Issues、PRs、Actions、Repos",
                version="1.0.0",
                category="community",
                transport="http",
                endpoint="https://api.github.com",
                tools=[
                    {"name": "create_issue", "description": "创建 Issue"},
                    {"name": "create_pr", "description": "创建 PR"},
                    {"name": "list_repos", "description": "列出仓库"},
                    {"name": "get_actions", "description": "查看 CI 状态"},
                ],
                installed=False,
            ),
            MCPServerInfo(
                id="database",
                name="Database",
                description="数据库操作 — SQL 查询、Schema 浏览",
                version="0.1.0",
                category="community",
                transport="stdio",
                tools=[
                    {"name": "query", "description": "执行 SQL 查询"},
                    {"name": "list_tables", "description": "列出表"},
                    {"name": "describe_table", "description": "表结构"},
                ],
                installed=False,
            ),
            MCPServerInfo(
                id="docker",
                name="Docker",
                description="Docker 容器管理 — 构建、运行、日志",
                version="0.1.0",
                category="community",
                transport="stdio",
                tools=[
                    {"name": "docker_build", "description": "构建镜像"},
                    {"name": "docker_run", "description": "运行容器"},
                    {"name": "docker_logs", "description": "查看日志"},
                    {"name": "docker_ps", "description": "列出容器"},
                ],
                installed=False,
            ),
            MCPServerInfo(
                id="slack",
                name="Slack",
                description="Slack 消息 — 发送通知、监听频道",
                version="0.1.0",
                category="community",
                transport="http",
                tools=[
                    {"name": "send_message", "description": "发送消息"},
                    {"name": "list_channels", "description": "列出频道"},
                ],
                installed=False,
            ),
        ]
        for s in servers:
            self._servers[s.id] = s

    def list_servers(self, category: str | None = None) -> list[MCPServerInfo]:
        """列出所有 MCP Server."""
        servers = list(self._servers.values())
        if category:
            servers = [s for s in servers if s.category == category]
        return servers

    def get_server(self, server_id: str) -> MCPServerInfo | None:
        return self._servers.get(server_id)

    def install_server(self, server_id: str) -> MCPServerInfo | None:
        """安装 MCP Server."""
        server = self._servers.get(server_id)
        if server:
            server.installed = True
            server.enabled = True
            logger.info("MCP Server 已安装: %s", server.name)
        return server

    def uninstall_server(self, server_id: str) -> bool:
        server = self._servers.get(server_id)
        if server and server.category != "builtin":
            server.installed = False
            server.enabled = False
            return True
        return False

    def toggle_server(self, server_id: str, enabled: bool) -> MCPServerInfo | None:
        server = self._servers.get(server_id)
        if server:
            server.enabled = enabled
        return server

    def get_installed_tools(self) -> list[dict]:
        """获取所有已安装 Server 的工具列表."""
        tools = []
        for s in self._servers.values():
            if s.installed and s.enabled:
                for t in s.tools:
                    tools.append({
                        "server_id": s.id,
                        "server_name": s.name,
                        **t,
                    })
        return tools


mcp_marketplace = MCPMarketplace()
