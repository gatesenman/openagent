"""代码搜索工具 / Code search tool.

在沙箱虚拟环境中搜索代码。
"""

from app.agent.tools.base import BaseTool, ToolResult
from app.sandbox.base import BaseSandbox


class SearchCodeTool(BaseTool):
    """在沙箱内搜索代码."""

    name = "search_code"
    description = "Search for patterns in code files within the sandbox. Uses grep/ripgrep."
    description_zh = "在沙箱虚拟环境中搜索代码模式。使用 grep/ripgrep。"
    parameters = {
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Search pattern (regex) / 搜索模式（正则表达式）",
            },
            "path": {
                "type": "string",
                "description": "Directory to search in (default: workspace) / 搜索目录",
            },
            "file_pattern": {
                "type": "string",
                "description": "File glob pattern (e.g., '*.py') / 文件匹配模式",
            },
            "case_insensitive": {
                "type": "boolean",
                "description": "Case insensitive search / 忽略大小写",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum results (default: 50) / 最大结果数",
            },
        },
        "required": ["pattern"],
    }

    async def execute(self, sandbox: BaseSandbox, args: dict) -> ToolResult:
        pattern = args["pattern"]
        path = args.get("path", "/workspace")
        file_pattern = args.get("file_pattern")
        case_insensitive = args.get("case_insensitive", False)
        max_results = args.get("max_results", 50)

        # 构建 grep 命令
        cmd_parts = ["grep", "-rn"]
        if case_insensitive:
            cmd_parts.append("-i")
        if file_pattern:
            cmd_parts.extend(["--include", file_pattern])

        cmd_parts.extend([f"'{pattern}'", path])
        cmd_parts.append(f"| head -n {max_results}")

        cmd = " ".join(cmd_parts)

        result = await sandbox.exec_command(cmd, timeout=30)

        if result.exit_code == 0 and result.stdout.strip():
            matches = result.stdout.strip().split("\n")
            return ToolResult(
                success=True,
                output=result.stdout,
                metadata={"match_count": len(matches)},
            )
        elif result.exit_code == 1:
            return ToolResult(
                success=True,
                output="未找到匹配项",
                metadata={"match_count": 0},
            )
        else:
            return ToolResult(
                success=False,
                output="",
                error=f"搜索失败: {result.stderr}",
            )
