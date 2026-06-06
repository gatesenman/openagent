"""沙箱抽象基类 / Sandbox abstract base class.

定义所有沙箱实现必须遵循的接口。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import AsyncIterator


class SandboxStatus(str, Enum):
    """沙箱状态."""
    CREATING = "creating"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"
    DESTROYED = "destroyed"


class SandboxPlatform(str, Enum):
    """沙箱平台."""
    LINUX = "linux"
    WINDOWS = "windows"


@dataclass
class SandboxConfig:
    """沙箱配置."""
    platform: SandboxPlatform = SandboxPlatform.LINUX
    image: str = "ubuntu:22.04"
    cpu_limit: float = 2.0          # CPU 核数
    memory_limit: str = "4g"        # 内存限制
    disk_limit: str = "20g"         # 磁盘限制
    timeout: int = 3600             # 超时时间（秒）
    network_enabled: bool = True    # 是否允许网络
    ports: dict[int, int] = field(default_factory=dict)  # 端口映射
    env_vars: dict[str, str] = field(default_factory=dict)
    workspace_path: str = "/workspace"  # 沙箱内工作目录


@dataclass
class ExecResult:
    """命令执行结果."""
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: int


@dataclass
class FileInfo:
    """文件信息."""
    path: str
    name: str
    is_dir: bool
    size: int
    modified_at: str


class BaseSandbox(ABC):
    """沙箱抽象基类.

    所有沙箱实现（Docker/KVM/本地进程）必须实现此接口。
    Agent 的所有工具（shell_exec/file_read/file_write）都通过沙箱执行。
    """

    def __init__(self, sandbox_id: str, config: SandboxConfig):
        self.sandbox_id = sandbox_id
        self.config = config
        self.status = SandboxStatus.CREATING

    @abstractmethod
    async def create(self) -> None:
        """创建并启动沙箱环境."""

    @abstractmethod
    async def destroy(self) -> None:
        """销毁沙箱环境并清理资源."""

    @abstractmethod
    async def exec_command(
        self, command: str, timeout: int | None = None, workdir: str | None = None
    ) -> ExecResult:
        """在沙箱中执行命令."""

    @abstractmethod
    async def exec_stream(
        self, command: str, timeout: int | None = None, workdir: str | None = None
    ) -> AsyncIterator[str]:
        """在沙箱中流式执行命令（用于终端面板实时输出）."""

    @abstractmethod
    async def read_file(self, path: str) -> str:
        """读取沙箱内文件."""

    @abstractmethod
    async def write_file(self, path: str, content: str) -> None:
        """写入沙箱内文件."""

    @abstractmethod
    async def list_files(self, path: str = "/workspace") -> list[FileInfo]:
        """列出沙箱内目录."""

    @abstractmethod
    async def upload_file(self, local_path: str, remote_path: str) -> None:
        """上传文件到沙箱."""

    @abstractmethod
    async def download_file(self, remote_path: str, local_path: str) -> None:
        """从沙箱下载文件."""

    @abstractmethod
    async def get_status(self) -> SandboxStatus:
        """获取沙箱状态."""

    @abstractmethod
    async def pause(self) -> None:
        """暂停沙箱."""

    @abstractmethod
    async def resume(self) -> None:
        """恢复沙箱."""

    @abstractmethod
    async def snapshot(self) -> str:
        """创建沙箱快照，返回快照ID."""

    @abstractmethod
    async def restore(self, snapshot_id: str) -> None:
        """从快照恢复沙箱."""
