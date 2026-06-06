"""本地进程沙箱 / Local process sandbox.

用于 localhost 模式：不使用 Docker，直接在本地子进程中执行。
适用于开发环境和轻量级测试场景。
"""

import asyncio
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import AsyncIterator

from app.sandbox.base import (
    BaseSandbox,
    ExecResult,
    FileInfo,
    SandboxConfig,
    SandboxStatus,
)

logger = logging.getLogger(__name__)


class LocalSandbox(BaseSandbox):
    """本地进程沙箱.

    在本地文件系统中创建隔离的工作目录，
    使用子进程执行命令。适用于 localhost 模式。
    """

    def __init__(self, sandbox_id: str, config: SandboxConfig):
        super().__init__(sandbox_id, config)
        self.workspace: Path | None = None

    async def create(self) -> None:
        """创建本地工作目录."""
        self.workspace = Path(tempfile.mkdtemp(prefix=f"openagent-{self.sandbox_id}-"))
        self.status = SandboxStatus.RUNNING
        logger.info("本地沙箱已创建: %s", self.workspace)

    async def destroy(self) -> None:
        """清理工作目录."""
        if self.workspace and self.workspace.exists():
            import shutil
            shutil.rmtree(self.workspace, ignore_errors=True)
        self.status = SandboxStatus.DESTROYED
        logger.info("本地沙箱已销毁: %s", self.workspace)

    async def exec_command(
        self, command: str, timeout: int | None = None, workdir: str | None = None
    ) -> ExecResult:
        """在本地子进程中执行命令."""
        work = workdir or str(self.workspace)
        effective_timeout = timeout or self.config.timeout
        start = time.monotonic()

        try:
            proc = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=work,
            )
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                proc.communicate(), timeout=effective_timeout
            )
            duration_ms = int((time.monotonic() - start) * 1000)
            return ExecResult(
                exit_code=proc.returncode or 0,
                stdout=stdout_bytes.decode("utf-8", errors="replace"),
                stderr=stderr_bytes.decode("utf-8", errors="replace"),
                duration_ms=duration_ms,
            )
        except asyncio.TimeoutError:
            duration_ms = int((time.monotonic() - start) * 1000)
            return ExecResult(
                exit_code=-1,
                stdout="",
                stderr=f"Command timed out after {effective_timeout}s",
                duration_ms=duration_ms,
            )

    async def exec_stream(
        self, command: str, timeout: int | None = None, workdir: str | None = None
    ) -> AsyncIterator[str]:
        """流式执行命令."""
        work = workdir or str(self.workspace)

        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            cwd=work,
        )

        if proc.stdout:
            async for line in proc.stdout:
                yield line.decode("utf-8", errors="replace")

        await proc.wait()

    async def read_file(self, path: str) -> str:
        """读取本地文件."""
        full_path = self._resolve_path(path)
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return full_path.read_text(encoding="utf-8")

    async def write_file(self, path: str, content: str) -> None:
        """写入本地文件."""
        full_path = self._resolve_path(path)
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

    async def list_files(self, path: str = "/workspace") -> list[FileInfo]:
        """列出本地目录."""
        dir_path = self._resolve_path(path)
        if not dir_path.exists():
            return []

        files = []
        for item in dir_path.iterdir():
            stat = item.stat()
            files.append(FileInfo(
                path=str(item),
                name=item.name,
                is_dir=item.is_dir(),
                size=stat.st_size,
                modified_at=str(stat.st_mtime),
            ))
        return files

    async def upload_file(self, local_path: str, remote_path: str) -> None:
        """复制文件到工作目录."""
        import shutil
        dest = self._resolve_path(remote_path)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(local_path, dest)

    async def download_file(self, remote_path: str, local_path: str) -> None:
        """从工作目录复制文件."""
        import shutil
        src = self._resolve_path(remote_path)
        shutil.copy2(src, local_path)

    async def get_status(self) -> SandboxStatus:
        """获取状态."""
        return self.status

    async def pause(self) -> None:
        """暂停（本地模式仅标记状态）."""
        self.status = SandboxStatus.PAUSED

    async def resume(self) -> None:
        """恢复."""
        self.status = SandboxStatus.RUNNING

    async def snapshot(self) -> str:
        """创建快照（复制工作目录）."""
        import shutil
        snapshot_dir = f"{self.workspace}_snapshot_{int(time.time())}"
        shutil.copytree(str(self.workspace), snapshot_dir)
        return snapshot_dir

    async def restore(self, snapshot_id: str) -> None:
        """从快照恢复."""
        import shutil
        if self.workspace and self.workspace.exists():
            shutil.rmtree(self.workspace)
        shutil.copytree(snapshot_id, str(self.workspace))

    def _resolve_path(self, path: str) -> Path:
        """解析路径，确保在工作目录内."""
        if not self.workspace:
            raise RuntimeError("Sandbox not initialized")

        if os.path.isabs(path):
            # 绝对路径：映射到工作目录下
            resolved = self.workspace / path.lstrip("/")
        else:
            resolved = self.workspace / path

        return resolved
