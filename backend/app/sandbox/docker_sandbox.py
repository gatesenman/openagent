"""Docker 容器沙箱实现 / Docker container sandbox.

Phase 1 沙箱实现：每个 Session 对应一个 Docker 容器。
Agent 的所有操作（执行命令/读写文件/Git操作）都在容器内完成。
"""

import asyncio
import json
import logging
import time
from typing import AsyncIterator

from app.sandbox.base import (
    BaseSandbox,
    ExecResult,
    FileInfo,
    SandboxConfig,
    SandboxStatus,
)

logger = logging.getLogger(__name__)


class DockerSandbox(BaseSandbox):
    """Docker 容器沙箱.

    使用 Docker CLI 管理容器生命周期。
    每个 Agent Session 创建一个隔离的容器环境。
    """

    def __init__(self, sandbox_id: str, config: SandboxConfig):
        super().__init__(sandbox_id, config)
        self.container_name = f"openagent-sandbox-{sandbox_id}"
        self.container_id: str | None = None

    async def create(self) -> None:
        """创建并启动 Docker 容器."""
        port_args = []
        for host_port, container_port in self.config.ports.items():
            port_args.extend(["-p", f"{host_port}:{container_port}"])

        env_args = []
        for key, value in self.config.env_vars.items():
            env_args.extend(["-e", f"{key}={value}"])

        cmd = [
            "docker", "run", "-d",
            "--name", self.container_name,
            "--cpus", str(self.config.cpu_limit),
            "--memory", self.config.memory_limit,
            "-w", self.config.workspace_path,
            *port_args,
            *env_args,
            self.config.image,
            "sleep", "infinity",  # 保持容器运行
        ]

        result = await self._run_host_command(cmd)
        if result.exit_code == 0:
            self.container_id = result.stdout.strip()[:12]
            self.status = SandboxStatus.RUNNING
            logger.info("容器已创建: %s (%s)", self.container_name, self.container_id)

            # 初始化工作目录
            await self.exec_command(f"mkdir -p {self.config.workspace_path}")
            # 安装基础工具
            await self.exec_command(
                "apt-get update -qq && apt-get install -y -qq git curl wget vim > /dev/null 2>&1"
            )
        else:
            self.status = SandboxStatus.ERROR
            logger.error("容器创建失败: %s", result.stderr)
            raise RuntimeError(f"Failed to create sandbox: {result.stderr}")

    async def destroy(self) -> None:
        """销毁容器."""
        await self._run_host_command(
            ["docker", "rm", "-f", self.container_name]
        )
        self.status = SandboxStatus.DESTROYED
        logger.info("容器已销毁: %s", self.container_name)

    async def exec_command(
        self, command: str, timeout: int | None = None, workdir: str | None = None
    ) -> ExecResult:
        """在容器中执行命令."""
        work = workdir or self.config.workspace_path
        cmd = [
            "docker", "exec",
            "-w", work,
            self.container_name,
            "bash", "-c", command,
        ]

        effective_timeout = timeout or self.config.timeout
        start = time.monotonic()

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
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
        """流式执行命令（用于终端面板实时输出）."""
        work = workdir or self.config.workspace_path
        cmd = [
            "docker", "exec",
            "-w", work,
            self.container_name,
            "bash", "-c", command,
        ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        if proc.stdout:
            async for line in proc.stdout:
                yield line.decode("utf-8", errors="replace")

        await proc.wait()

    async def read_file(self, path: str) -> str:
        """读取容器内文件."""
        result = await self.exec_command(f"cat '{path}'")
        if result.exit_code != 0:
            raise FileNotFoundError(f"File not found in sandbox: {path}")
        return result.stdout

    async def write_file(self, path: str, content: str) -> None:
        """写入容器内文件."""
        # 确保父目录存在
        parent = "/".join(path.rsplit("/", 1)[:-1])
        if parent:
            await self.exec_command(f"mkdir -p '{parent}'")

        escaped = content.replace("'", "'\\''")
        result = await self.exec_command(f"cat > '{path}' << 'OPENAGENT_EOF'\n{escaped}\nOPENAGENT_EOF")
        if result.exit_code != 0:
            raise IOError(f"Failed to write file: {result.stderr}")

    async def list_files(self, path: str = "/workspace") -> list[FileInfo]:
        """列出容器内目录."""
        result = await self.exec_command(
            f"find '{path}' -maxdepth 1 -printf '%y\\t%s\\t%T@\\t%p\\n' 2>/dev/null | tail -n +2"
        )
        files = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("\t", 3)
            if len(parts) == 4:
                file_type, size, mtime, filepath = parts
                name = filepath.rsplit("/", 1)[-1] if "/" in filepath else filepath
                files.append(FileInfo(
                    path=filepath,
                    name=name,
                    is_dir=(file_type == "d"),
                    size=int(size) if size.isdigit() else 0,
                    modified_at=mtime,
                ))
        return files

    async def upload_file(self, local_path: str, remote_path: str) -> None:
        """上传文件到容器."""
        await self._run_host_command(
            ["docker", "cp", local_path, f"{self.container_name}:{remote_path}"]
        )

    async def download_file(self, remote_path: str, local_path: str) -> None:
        """从容器下载文件."""
        await self._run_host_command(
            ["docker", "cp", f"{self.container_name}:{remote_path}", local_path]
        )

    async def get_status(self) -> SandboxStatus:
        """获取容器状态."""
        result = await self._run_host_command(
            ["docker", "inspect", "-f", "{{.State.Status}}", self.container_name]
        )
        status_map = {
            "running": SandboxStatus.RUNNING,
            "paused": SandboxStatus.PAUSED,
            "exited": SandboxStatus.STOPPED,
            "dead": SandboxStatus.ERROR,
        }
        docker_status = result.stdout.strip()
        self.status = status_map.get(docker_status, SandboxStatus.ERROR)
        return self.status

    async def pause(self) -> None:
        """暂停容器."""
        await self._run_host_command(["docker", "pause", self.container_name])
        self.status = SandboxStatus.PAUSED

    async def resume(self) -> None:
        """恢复容器."""
        await self._run_host_command(["docker", "unpause", self.container_name])
        self.status = SandboxStatus.RUNNING

    async def snapshot(self) -> str:
        """创建容器快照（Docker commit）."""
        snapshot_tag = f"openagent-snapshot-{self.sandbox_id}:{int(time.time())}"
        await self._run_host_command(
            ["docker", "commit", self.container_name, snapshot_tag]
        )
        logger.info("快照已创建: %s", snapshot_tag)
        return snapshot_tag

    async def restore(self, snapshot_id: str) -> None:
        """从快照恢复（销毁当前容器，从快照镜像重建）."""
        await self.destroy()
        old_image = self.config.image
        self.config.image = snapshot_id
        await self.create()
        self.config.image = old_image

    async def _run_host_command(self, cmd: list[str]) -> ExecResult:
        """在宿主机执行命令."""
        start = time.monotonic()
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout_bytes, stderr_bytes = await proc.communicate()
        duration_ms = int((time.monotonic() - start) * 1000)
        return ExecResult(
            exit_code=proc.returncode or 0,
            stdout=stdout_bytes.decode("utf-8", errors="replace"),
            stderr=stderr_bytes.decode("utf-8", errors="replace"),
            duration_ms=duration_ms,
        )
