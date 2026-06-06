"""工具服务 / Tool service.

管理和执行 Agent 工具。
所有工具都在沙箱虚拟环境中执行。
"""

import logging
from typing import Any

from app.agent.tools.base import BaseTool, ToolResult
from app.agent.tools.file_ops import FileReadTool, FileWriteTool
from app.agent.tools.git_ops import GitOpsTool
from app.agent.tools.search_code import SearchCodeTool
from app.agent.tools.shell_exec import ShellExecTool
from app.agent.validators import OutputValidator
from app.sandbox.base import BaseSandbox
from app.sandbox.manager import sandbox_manager

logger = logging.getLogger(__name__)


class ToolService:
    """工具服务.

    管理所有可用工具，并在沙箱中执行。
    支持内置工具和 MCP 外部工具。
    """

    def __init__(self):
        self.validator = OutputValidator()
        self._tools: dict[str, BaseTool] = {}
        self._register_builtin_tools()

    def _register_builtin_tools(self) -> None:
        """注册内置工具."""
        builtins = [
            ShellExecTool(),
            FileReadTool(),
            FileWriteTool(),
            SearchCodeTool(),
            GitOpsTool(),
        ]
        for tool in builtins:
            self._tools[tool.name] = tool

    def register_tool(self, tool: BaseTool) -> None:
        """注册自定义工具."""
        self._tools[tool.name] = tool
        logger.info("工具已注册: %s", tool.name)

    def list_tools(self) -> list[dict[str, Any]]:
        """列出所有可用工具."""
        return [
            {
                "name": t.name,
                "description": t.description,
                "description_zh": t.description_zh,
                "parameters": t.parameters,
                "category": t.category,
            }
            for t in self._tools.values()
        ]

    def get_tool(self, name: str) -> BaseTool | None:
        """获取工具."""
        return self._tools.get(name)

    async def execute_tool(
        self,
        session_id: str,
        tool_name: str,
        arguments: dict,
    ) -> ToolResult:
        """在沙箱中执行工具.

        Args:
            session_id: 会话ID（用于获取对应沙箱）
            tool_name: 工具名称
            arguments: 工具参数
        """
        tool = self._tools.get(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                output="",
                error=f"未知工具: {tool_name}",
            )

        # 参数验证
        validation = self.validator.validate_tool_call(
            tool_name, arguments, tool.parameters
        )
        if not validation.valid:
            return ToolResult(
                success=False,
                output="",
                error=f"参数验证失败: {'; '.join(validation.errors)}",
            )

        # 获取沙箱
        sandbox = await sandbox_manager.get_sandbox(session_id)
        if not sandbox:
            return ToolResult(
                success=False,
                output="",
                error="沙箱不可用，请先创建会话",
            )

        # 在沙箱中执行
        try:
            result = await tool.execute(sandbox, arguments)

            # 检查输出是否包含敏感信息
            if result.success and result.output:
                sensitivity = self.validator.check_sensitive_output(result.output)
                if sensitivity.warnings:
                    logger.warning(
                        "工具输出包含敏感信息: %s - %s",
                        tool_name, sensitivity.warnings,
                    )

            return result
        except Exception as e:
            logger.error("工具执行异常: %s - %s", tool_name, e)
            return ToolResult(
                success=False,
                output="",
                error=f"工具执行异常: {e}",
            )

    def get_openai_tools(self) -> list[dict]:
        """获取 OpenAI function calling 格式的工具列表."""
        return [t.to_openai_function() for t in self._tools.values()]

    def get_mcp_tools(self) -> list[dict]:
        """获取 MCP 格式的工具列表."""
        return [t.to_mcp_tool() for t in self._tools.values()]


# 全局单例
tool_service = ToolService()
