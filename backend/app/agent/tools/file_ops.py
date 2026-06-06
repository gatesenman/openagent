"""文件操作工具 / File operation tools.

在沙箱虚拟环境中读写文件。
"""

from app.agent.tools.base import BaseTool, ToolResult
from app.sandbox.base import BaseSandbox


class FileReadTool(BaseTool):
    """读取沙箱内文件."""

    name = "file_read"
    description = "Read a file from the sandbox environment. Supports reading specific line ranges."
    description_zh = "读取沙箱虚拟环境中的文件。支持指定行范围读取。"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "File path to read / 文件路径",
            },
            "start_line": {
                "type": "integer",
                "description": "Start line number (1-based, optional) / 起始行号",
            },
            "end_line": {
                "type": "integer",
                "description": "End line number (inclusive, optional) / 结束行号",
            },
        },
        "required": ["path"],
    }

    async def execute(self, sandbox: BaseSandbox, args: dict) -> ToolResult:
        path = args["path"]
        start_line = args.get("start_line")
        end_line = args.get("end_line")

        try:
            content = await sandbox.read_file(path)

            if start_line or end_line:
                lines = content.split("\n")
                start = (start_line or 1) - 1
                end = end_line or len(lines)
                content = "\n".join(lines[start:end])

            return ToolResult(
                success=True,
                output=content,
                metadata={"path": path, "lines": len(content.split("\n"))},
            )
        except FileNotFoundError:
            return ToolResult(
                success=False,
                output="",
                error=f"文件不存在: {path}",
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"读取文件失败: {e}",
            )


class FileWriteTool(BaseTool):
    """写入沙箱内文件."""

    name = "file_write"
    description = "Write content to a file in the sandbox environment. Creates parent directories if needed."
    description_zh = "在沙箱虚拟环境中写入文件。如有需要会自动创建父目录。"
    parameters = {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "File path to write / 文件路径",
            },
            "content": {
                "type": "string",
                "description": "Content to write / 文件内容",
            },
        },
        "required": ["path", "content"],
    }

    async def execute(self, sandbox: BaseSandbox, args: dict) -> ToolResult:
        path = args["path"]
        content = args["content"]

        try:
            await sandbox.write_file(path, content)
            return ToolResult(
                success=True,
                output=f"文件已写入: {path} ({len(content)} bytes)",
                metadata={"path": path, "size": len(content)},
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=f"写入文件失败: {e}",
            )
