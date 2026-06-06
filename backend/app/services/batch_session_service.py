"""批量会话服务 / Batch Session Service.

支持:
- 大任务自动拆分为子任务
- 多个子 Agent 并行执行 (各自独立沙箱)
- 自动合并结果 + 冲突解决
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class BatchStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"  # 部分完成
    FAILED = "failed"


@dataclass
class SubTask:
    """子任务."""
    id: str = ""
    batch_id: str = ""
    session_id: str = ""
    title: str = ""
    prompt: str = ""
    status: str = "pending"
    result: str = ""
    created_at: float = 0.0
    completed_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class BatchSession:
    """批量会话."""
    id: str = ""
    parent_session_id: str = ""
    title: str = ""
    description: str = ""
    status: BatchStatus = BatchStatus.PENDING
    subtasks: list[SubTask] = field(default_factory=list)
    merge_strategy: str = "auto"  # auto / manual / sequential
    created_at: float = 0.0
    completed_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = time.time()


class BatchSessionService:
    """批量会话管理."""

    def __init__(self):
        self._batches: dict[str, BatchSession] = {}

    def create_batch(
        self,
        parent_session_id: str,
        title: str,
        subtask_prompts: list[dict],
        merge_strategy: str = "auto",
    ) -> BatchSession:
        """创建批量会话."""
        batch = BatchSession(
            parent_session_id=parent_session_id,
            title=title,
            merge_strategy=merge_strategy,
        )

        for sp in subtask_prompts:
            subtask = SubTask(
                batch_id=batch.id,
                title=sp.get("title", ""),
                prompt=sp.get("prompt", ""),
            )
            batch.subtasks.append(subtask)

        self._batches[batch.id] = batch
        logger.info("批量会话已创建: %s, 子任务数: %d", batch.id, len(batch.subtasks))
        return batch

    def start_batch(self, batch_id: str) -> BatchSession | None:
        """启动批量执行."""
        batch = self._batches.get(batch_id)
        if not batch:
            return None
        batch.status = BatchStatus.RUNNING
        for st in batch.subtasks:
            st.status = "running"
            st.session_id = str(uuid.uuid4())  # Phase 2: 实际创建子会话
        return batch

    def update_subtask(self, batch_id: str, subtask_id: str, status: str, result: str = "") -> bool:
        """更新子任务状态."""
        batch = self._batches.get(batch_id)
        if not batch:
            return False
        for st in batch.subtasks:
            if st.id == subtask_id:
                st.status = status
                st.result = result
                if status in ("completed", "failed"):
                    st.completed_at = time.time()
                self._check_batch_completion(batch)
                return True
        return False

    def _check_batch_completion(self, batch: BatchSession):
        """检查批量是否全部完成."""
        total = len(batch.subtasks)
        completed = sum(1 for st in batch.subtasks if st.status == "completed")
        failed = sum(1 for st in batch.subtasks if st.status == "failed")

        if completed + failed == total:
            if failed == 0:
                batch.status = BatchStatus.COMPLETED
            elif completed > 0:
                batch.status = BatchStatus.PARTIAL
            else:
                batch.status = BatchStatus.FAILED
            batch.completed_at = time.time()

    def get_batch(self, batch_id: str) -> dict | None:
        """获取批量会话详情."""
        batch = self._batches.get(batch_id)
        if not batch:
            return None
        return {
            "id": batch.id,
            "title": batch.title,
            "status": batch.status.value,
            "merge_strategy": batch.merge_strategy,
            "subtasks": [
                {
                    "id": st.id,
                    "title": st.title,
                    "status": st.status,
                    "session_id": st.session_id,
                    "result": st.result[:200] if st.result else "",
                }
                for st in batch.subtasks
            ],
            "progress": {
                "total": len(batch.subtasks),
                "completed": sum(1 for st in batch.subtasks if st.status == "completed"),
                "running": sum(1 for st in batch.subtasks if st.status == "running"),
                "failed": sum(1 for st in batch.subtasks if st.status == "failed"),
            },
        }

    def list_batches(self, parent_session_id: str = "") -> list[dict]:
        """列出批量会话."""
        results = []
        for b in self._batches.values():
            if parent_session_id and b.parent_session_id != parent_session_id:
                continue
            results.append({
                "id": b.id,
                "title": b.title,
                "status": b.status.value,
                "subtask_count": len(b.subtasks),
                "created_at": b.created_at,
            })
        return results


batch_session_service = BatchSessionService()
