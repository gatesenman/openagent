"""Shell 命令执行工具 / Shell execution tool.

在沙箱虚拟环境中执行 shell 命令。
包含安全检查：拦截危险命令。
"""

import re

from app.agent.tools.base import BaseTool, ToolResult
from app.sandbox.base import BaseSandbox

DANGEROUS_PATTERNS = [
    r"rm\s+-rf\s+/\s*$",
    r"rm\s+-rf\s+/\*",
    r"mkfs\.",
    r"dd\s+if=.*of=/dev/",
    r":(){ :\|:& };:",
    r"chmod\s+-R\s+777\s+/",
    r">\s*/dev/sda",
    r"curl.*\|\s*bash",
    r"wget.*\|\s*bash",
]


class ShellExecTool(BaseTool):
    """在沙箱中执行 Shell 命令."""

    name = "shell_exec"
    description = "Execute a shell command in the sandbox environment. Returns stdout, stderr, and exit code."
    description_zh = "在沙箱虚拟环境中执行 Shell 命令。返回标准输出、标准错误和退出码。"
    parameters = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute / 要执行的 Shell 命令",
            },
            "workdir": {
                "type": "string",
                "description": "Working directory (optional) / 工作目录（可选）",
            },
            "timeout": {
                "type": "integer",
                "description": "Timeout in seconds (default: 300) / 超时时间（秒，默认300）",
            },
        },
        "required": ["command"],
    }

    async def execute(self, sandbox: BaseSandbox, args: dict) -> ToolResult:
        command = args["command"]
        workdir = args.get("workdir")
        timeout = args.get("timeout", 300)

        # 安全检查
        danger = self._check_dangerous(command)
        if danger:
            return ToolResult(
                success=False,
                output="",
                error=f"命令被安全策略拦截: {danger}",
            )

        result = await sandbox.exec_command(
            command=command,
            timeout=timeout,
            workdir=workdir,
        )

        return ToolResult(
            success=(result.exit_code == 0),
            output=result.stdout,
            error=result.stderr if result.exit_code != 0 else None,
            duration_ms=result.duration_ms,
            metadata={"exit_code": result.exit_code},
        )

    def _check_dangerous(self, command: str) -> str | None:
        """检查是否包含危险命令."""
        for pattern in DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return f"Matched dangerous pattern: {pattern}"
        return None
