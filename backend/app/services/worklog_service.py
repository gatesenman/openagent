"""Worklog 增强服务 / Enhanced Worklog Service.

Agent 操作时间线记录与回放:
- 每个 Agent 动作记录为 WorklogEntry
- 支持时间线查询和过滤
- 支持回放模式（按时间序列重放事件）
- 关键时刻注释标记
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class WorklogCategory(str, Enum):
    THINK = "think"        # Agent 思考
    TOOL_CALL = "tool_call"  # 工具调用
    TOOL_RESULT = "tool_result"  # 工具结果
    CODE_EDIT = "code_edit"   # 代码编辑
    COMMAND = "command"      # Shell 命令
    GIT = "git"             # Git 操作
    ERROR = "error"         # 错误
    MILESTONE = "milestone"  # 里程碑
    USER = "user"           # 用户消息


@dataclass
class WorklogEntry:
    """Worklog 条目."""
    id: str = ""
    session_id: str = ""
    category: WorklogCategory = WorklogCategory.TOOL_CALL
    title: str = ""
    detail: str = ""
    timestamp: float = 0.0
    duration_ms: int = 0
    metadata: dict = field(default_factory=dict)
    annotations: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class ReplayState:
    """回放状态."""
    session_id: str = ""
    entries: list[WorklogEntry] = field(default_factory=list)
    current_index: int = 0
    speed: float = 1.0
    paused: bool = False


class WorklogService:
    """Worklog 增强服务."""

    def __init__(self):
        self._entries: dict[str, list[WorklogEntry]] = {}  # session_id → entries
        self._replays: dict[str, ReplayState] = {}

    def log(
        self,
        session_id: str,
        category: WorklogCategory | str,
        title: str,
        detail: str = "",
        duration_ms: int = 0,
        metadata: dict | None = None,
    ) -> WorklogEntry:
        """记录 Worklog 条目."""
        if isinstance(category, str):
            category = WorklogCategory(category)
        entry = WorklogEntry(
            session_id=session_id,
            category=category,
            title=title,
            detail=detail,
            duration_ms=duration_ms,
            metadata=metadata or {},
        )
        self._entries.setdefault(session_id, []).append(entry)
        return entry

    def get_timeline(
        self,
        session_id: str,
        category: str = "",
        since: float = 0,
        limit: int = 100,
    ) -> list[dict]:
        """获取时间线."""
        entries = self._entries.get(session_id, [])
        if category:
            entries = [e for e in entries if e.category.value == category]
        if since:
            entries = [e for e in entries if e.timestamp >= since]
        return [
            {
                "id": e.id,
                "category": e.category.value,
                "title": e.title,
                "detail": e.detail[:200],
                "timestamp": e.timestamp,
                "duration_ms": e.duration_ms,
                "annotations": e.annotations,
            }
            for e in entries[-limit:]
        ]

    def annotate(self, entry_id: str, session_id: str, text: str) -> bool:
        """为条目添加注释."""
        for entry in self._entries.get(session_id, []):
            if entry.id == entry_id:
                entry.annotations.append(text)
                return True
        return False

    def start_replay(self, session_id: str, speed: float = 1.0) -> ReplayState:
        """开始回放."""
        entries = self._entries.get(session_id, [])
        state = ReplayState(
            session_id=session_id,
            entries=entries,
            speed=speed,
        )
        self._replays[session_id] = state
        return state

    def replay_next(self, session_id: str) -> dict | None:
        """获取回放的下一个事件."""
        state = self._replays.get(session_id)
        if not state or state.current_index >= len(state.entries):
            return None
        entry = state.entries[state.current_index]
        state.current_index += 1
        return {
            "entry": {
                "id": entry.id,
                "category": entry.category.value,
                "title": entry.title,
                "detail": entry.detail,
                "timestamp": entry.timestamp,
            },
            "index": state.current_index,
            "total": len(state.entries),
            "progress": state.current_index / len(state.entries),
        }

    def stop_replay(self, session_id: str):
        """停止回放."""
        self._replays.pop(session_id, None)

    def get_summary(self, session_id: str) -> dict:
        """获取 Worklog 摘要统计."""
        entries = self._entries.get(session_id, [])
        by_category: dict[str, int] = {}
        total_duration = 0
        for e in entries:
            by_category[e.category.value] = by_category.get(e.category.value, 0) + 1
            total_duration += e.duration_ms

        return {
            "session_id": session_id,
            "total_entries": len(entries),
            "by_category": by_category,
            "total_duration_ms": total_duration,
            "first_entry": entries[0].timestamp if entries else 0,
            "last_entry": entries[-1].timestamp if entries else 0,
        }

    def extract_milestones(self, session_id: str) -> list[dict]:
        """提取里程碑事件."""
        entries = self._entries.get(session_id, [])
        milestones = [
            e for e in entries
            if e.category == WorklogCategory.MILESTONE or e.annotations
        ]
        return [
            {"id": e.id, "title": e.title, "timestamp": e.timestamp, "annotations": e.annotations}
            for e in milestones
        ]


worklog_service = WorklogService()
