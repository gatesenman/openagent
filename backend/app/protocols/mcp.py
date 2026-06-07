"""MCP 协议集成 / Model Context Protocol integration.

实现 MCP Client 和 Server 骨架。
MCP 是 Agent 连接外部工具和数据源的标准协议。
参考: https://modelcontextprotocol.io/

核心概念:
- Tool: Agent 可调用的工具（带 JSON Schema 参数验证）
- Resource: Agent 可读取的数据源
- Prompt: 可复用的提示词模板
"""

import logging
from dataclasses import dataclass, field
from typing import Any

from app.protocols.jsonrpc import (
    JsonRpcErrorCode,
    JsonRpcRequest,
    JsonRpcResponse,
    JsonRpcRouter,
)

logger = logging.getLogger(__name__)

MCP_VERSION = "2025-03-26"


@dataclass
class MCPTool:
    """MCP 工具定义."""

    name: str
    description: str
    input_schema: dict  # JSON Schema
    annotations: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        result = {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
        }
        if self.annotations:
            result["annotations"] = self.annotations
        return result


@dataclass
class MCPResource:
    """MCP 资源定义."""

    uri: str
    name: str
    description: str = ""
    mime_type: str = "text/plain"

    def to_dict(self) -> dict:
        return {
            "uri": self.uri,
            "name": self.name,
            "description": self.description,
            "mimeType": self.mime_type,
        }


@dataclass
class MCPPrompt:
    """MCP 提示词模板."""

    name: str
    description: str = ""
    arguments: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "arguments": self.arguments,
        }


class MCPServer:
    """MCP Server — 暴露 OpenAgent 能力给外部 Agent/IDE.

    实现 MCP 标准方法:
    - initialize
    - tools/list, tools/call
    - resources/list, resources/read
    - prompts/list, prompts/get
    """

    def __init__(self, name: str = "openagent", version: str = "0.1.0"):
        self.name = name
        self.version = version
        self._tools: dict[str, MCPTool] = {}
        self._tool_handlers: dict[str, Any] = {}
        self._resources: dict[str, MCPResource] = {}
        self._prompts: dict[str, MCPPrompt] = {}
        self._router = JsonRpcRouter()
        self._setup_routes()

    def _setup_routes(self):
        """注册 MCP 标准方法."""

        @self._router.method("initialize")
        async def initialize(**kwargs):
            return {
                "protocolVersion": MCP_VERSION,
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {"subscribe": False, "listChanged": True},
                    "prompts": {"listChanged": True},
                },
                "serverInfo": {
                    "name": self.name,
                    "version": self.version,
                },
            }

        @self._router.method("tools/list")
        async def tools_list(**kwargs):
            return {"tools": [t.to_dict() for t in self._tools.values()]}

        @self._router.method("tools/call")
        async def tools_call(name: str, arguments: dict | None = None):
            handler = self._tool_handlers.get(name)
            if not handler:
                raise ValueError(f"工具不存在: {name}")
            result = await handler(**(arguments or {}))
            return {"content": [{"type": "text", "text": str(result)}]}

        @self._router.method("resources/list")
        async def resources_list(**kwargs):
            return {"resources": [r.to_dict() for r in self._resources.values()]}

        @self._router.method("prompts/list")
        async def prompts_list(**kwargs):
            return {"prompts": [p.to_dict() for p in self._prompts.values()]}

        @self._router.method("ping")
        async def ping():
            return {}

    def add_tool(self, tool: MCPTool, handler) -> None:
        """注册工具."""
        self._tools[tool.name] = tool
        self._tool_handlers[tool.name] = handler
        logger.info("MCP 工具已注册: %s", tool.name)

    def add_resource(self, resource: MCPResource) -> None:
        """注册资源."""
        self._resources[resource.uri] = resource

    def add_prompt(self, prompt: MCPPrompt) -> None:
        """注册提示词模板."""
        self._prompts[prompt.name] = prompt

    async def handle_request(self, request: JsonRpcRequest) -> JsonRpcResponse:
        """处理 MCP 请求."""
        return await self._router.handle(request)


class MCPClient:
    """MCP Client — 连接外部 MCP Server（工具市场）.

    Agent 通过 MCP Client 调用外部工具/数据源。
    支持 stdio 和 HTTP/SSE 两种传输方式。
    """

    def __init__(self):
        self._servers: dict[str, dict] = {}  # name -> {url, transport, capabilities}
        self._connected: dict[str, bool] = {}

    async def connect(
        self,
        name: str,
        url: str = "",
        transport: str = "stdio",
    ) -> dict:
        """连接到外部 MCP Server.

        Args:
            name: 服务器名称
            url: 服务器地址（HTTP/SSE 模式）
            transport: 传输方式 (stdio / http+sse)
        """
        self._servers[name] = {
            "url": url,
            "transport": transport,
            "capabilities": {},
        }
        self._connected[name] = True
        logger.info("MCP Client 已连接: %s (transport=%s)", name, transport)

        return {
            "server": name,
            "transport": transport,
            "status": "connected",
        }

    async def disconnect(self, name: str) -> None:
        """断开连接."""
        self._connected.pop(name, None)
        self._servers.pop(name, None)
        logger.info("MCP Client 已断开: %s", name)

    async def list_tools(self, server_name: str) -> list[dict]:
        """列出远程 Server 的工具."""
        if server_name not in self._connected:
            raise ValueError(f"未连接到服务器: {server_name}")
        # 实际实现中通过 JSON-RPC 调用 tools/list
        return []

    async def call_tool(
        self, server_name: str, tool_name: str, arguments: dict | None = None
    ) -> dict:
        """调用远程工具."""
        if server_name not in self._connected:
            raise ValueError(f"未连接到服务器: {server_name}")
        # 实际实现中通过 JSON-RPC 调用 tools/call
        logger.info(
            "MCP 远程工具调用: server=%s, tool=%s", server_name, tool_name
        )
        return {"content": [{"type": "text", "text": "工具调用占位响应"}]}

    def list_servers(self) -> list[dict]:
        """列出所有已连接的服务器."""
        return [
            {
                "name": name,
                "transport": info["transport"],
                "connected": self._connected.get(name, False),
            }
            for name, info in self._servers.items()
        ]


# 全局实例
mcp_server = MCPServer()
mcp_client = MCPClient()
