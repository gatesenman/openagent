"""Agent 工具基类 / Agent tool base class.

所有工具都在沙箱环境中执行，通过 BaseSandbox 接口访问。
工具定义遵循 MCP (Model Context Protocol) 规范。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from app.sandbox.base import BaseSandbox


@dataclass
class ToolResult:
    """工具执行结果."""
    success: bool
    output: str
    error: str | None = None
    duration_ms: int | None = None
    metadata: dict[str, Any] | None = None


class BaseTool(ABC):
    """工具基类（MCP兼容）.

    每个工具：
    1. 声明 name / description / parameters（JSON Schema）
    2. 在沙箱环境中执行
    3. 返回结构化结果
    """

    name: str = ""
    description: str = ""
    description_zh: str = ""
    parameters: dict = {}
    category: str = "builtin"

    @abstractmethod
    async def execute(self, sandbox: BaseSandbox, args: dict) -> ToolResult:
        """在沙箱中执行工具.

        Args:
            sandbox: 当前会话的沙箱实例
            args: 工具参数（已通过 JSON Schema 验证）
        """

    def to_openai_function(self) -> dict:
        """转换为 OpenAI function calling 格式."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }

    def to_mcp_tool(self) -> dict:
        """转换为 MCP Tool 格式."""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.parameters,
        }
