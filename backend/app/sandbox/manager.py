"""沙箱管理器 / Sandbox manager.

管理所有沙箱实例的生命周期。
每个 Session 对应一个沙箱实例。
"""

import logging
from typing import Dict

from app.sandbox.base import BaseSandbox, SandboxConfig, SandboxPlatform, SandboxStatus
from app.sandbox.docker_sandbox import DockerSandbox
from app.sandbox.local_sandbox import LocalSandbox

logger = logging.getLogger(__name__)


class SandboxManager:
    """沙箱管理器.

    负责:
    1. 根据 Session 配置创建对应类型的沙箱
    2. 管理沙箱池（预热/复用）
    3. 资源清理和回收
    """

    def __init__(self):
        self._sandboxes: Dict[str, BaseSandbox] = {}

    async def create_sandbox(
        self,
        session_id: str,
        mode: str = "cloud",
        platform: str = "linux",
        config: SandboxConfig | None = None,
    ) -> BaseSandbox:
        """为 Session 创建沙箱.

        Args:
            session_id: 会话ID
            mode: 运行模式 (localhost/cascade/cloud)
            platform: 平台 (linux/windows)
            config: 自定义配置（可选）
        """
        if session_id in self._sandboxes:
            return self._sandboxes[session_id]

        if config is None:
            config = SandboxConfig(
                platform=SandboxPlatform(platform),
            )

        # 根据模式选择沙箱类型
        if mode == "localhost":
            sandbox = LocalSandbox(session_id, config)
        else:
            # cascade 和 cloud 模式都使用 Docker 沙箱
            sandbox = DockerSandbox(session_id, config)

        await sandbox.create()
        self._sandboxes[session_id] = sandbox
        logger.info(
            "沙箱已创建: session=%s, mode=%s, type=%s",
            session_id, mode, type(sandbox).__name__
        )
        return sandbox

    async def get_sandbox(self, session_id: str) -> BaseSandbox | None:
        """获取 Session 对应的沙箱."""
        return self._sandboxes.get(session_id)

    async def destroy_sandbox(self, session_id: str) -> None:
        """销毁 Session 对应的沙箱."""
        sandbox = self._sandboxes.pop(session_id, None)
        if sandbox:
            await sandbox.destroy()
            logger.info("沙箱已销毁: session=%s", session_id)

    async def list_sandboxes(self) -> list[dict]:
        """列出所有活跃的沙箱."""
        result = []
        for session_id, sandbox in self._sandboxes.items():
            status = await sandbox.get_status()
            result.append({
                "session_id": session_id,
                "status": status.value,
                "type": type(sandbox).__name__,
                "platform": sandbox.config.platform.value,
            })
        return result

    async def cleanup_all(self) -> None:
        """清理所有沙箱（应用关闭时调用）."""
        for session_id in list(self._sandboxes.keys()):
            await self.destroy_sandbox(session_id)
        logger.info("所有沙箱已清理")


# 全局单例
sandbox_manager = SandboxManager()
