"""Git 操作工具 / Git operation tools.

在沙箱虚拟环境中执行 Git 操作。
"""

from app.agent.tools.base import BaseTool, ToolResult
from app.sandbox.base import BaseSandbox


class GitOpsTool(BaseTool):
    """在沙箱内执行 Git 操作."""

    name = "git_ops"
    description = "Execute Git operations in the sandbox: status, diff, add, commit, log, branch, checkout, clone."
    description_zh = "在沙箱虚拟环境中执行 Git 操作：status/diff/add/commit/log/branch/checkout/clone。"
    parameters = {
        "type": "object",
        "properties": {
            "operation": {
                "type": "string",
                "enum": ["status", "diff", "add", "commit", "log", "branch", "checkout", "clone", "push", "pull"],
                "description": "Git operation / Git 操作类型",
            },
            "args": {
                "type": "string",
                "description": "Additional arguments / 附加参数",
            },
            "workdir": {
                "type": "string",
                "description": "Repository directory / 仓库目录",
            },
        },
        "required": ["operation"],
    }

    async def execute(self, sandbox: BaseSandbox, args: dict) -> ToolResult:
        operation = args["operation"]
        extra_args = args.get("args", "")
        workdir = args.get("workdir")

        # 构建 git 命令
        cmd = f"git {operation}"
        if extra_args:
            cmd = f"{cmd} {extra_args}"

        result = await sandbox.exec_command(cmd, workdir=workdir, timeout=120)

        return ToolResult(
            success=(result.exit_code == 0),
            output=result.stdout,
            error=result.stderr if result.exit_code != 0 else None,
            duration_ms=result.duration_ms,
            metadata={"operation": operation, "exit_code": result.exit_code},
        )
