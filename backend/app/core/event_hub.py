"""事件中心 / Event Hub.

集中管理 Agent 事件广播, 支持 WebSocket + SSE 双通道推送。
参考 Devin 的 Worklog 实时更新机制。
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, AsyncIterator, Optional

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Agent 事件类型 (参考 AG-UI 协议)."""

    # Agent 生命周期
    AGENT_START = "agent.start"
    AGENT_THINKING = "agent.thinking"
    AGENT_ACTION = "agent.action"
    AGENT_OBSERVE = "agent.observe"
    AGENT_ERROR = "agent.error"
    AGENT_COMPLETE = "agent.complete"

    # 工具执行
    TOOL_CALL = "tool.call"
    TOOL_RESULT = "tool.result"
    TOOL_ERROR = "tool.error"

    # 沙箱
    SANDBOX_CREATED = "sandbox.created"
    SANDBOX_EXEC = "sandbox.exec"
    SANDBOX_OUTPUT = "sandbox.output"
    SANDBOX_DESTROYED = "sandbox.destroyed"

    # 文件
    FILE_READ = "file.read"
    FILE_WRITE = "file.write"
    FILE_DELETE = "file.delete"

    # Git
    GIT_COMMIT = "git.commit"
    GIT_PUSH = "git.push"
    GIT_PR = "git.pr"

    # 系统
    SESSION_CREATED = "session.created"
    SESSION_UPDATED = "session.updated"
    MESSAGE = "message"
    HEARTBEAT = "heartbeat"


@dataclass
class AgentEvent:
    """Agent 事件."""

    type: EventType
    session_id: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    event_id: str = ""

    def __post_init__(self) -> None:
        if not self.event_id:
            import uuid
            self.event_id = str(uuid.uuid4())

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["type"] = self.type.value
        return d

    def to_sse(self) -> str:
        return f"event: {self.type.value}\ndata: {json.dumps(self.to_dict(), ensure_ascii=False)}\n\n"


class EventHub:
    """全局事件中心.

    管理所有 session 的事件订阅/广播:
    - subscribe(session_id): 获取事件异步迭代器
    - publish(event): 广播事件给所有该 session 的订阅者
    - history(session_id): 获取 session 历史事件 (Worklog)
    """

    def __init__(self, max_history: int = 1000) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[AgentEvent]]] = {}
        self._history: dict[str, list[AgentEvent]] = {}
        self._max_history = max_history

    async def publish(self, event: AgentEvent) -> None:
        """发布事件到所有订阅者."""
        sid = event.session_id

        # 存入历史
        if sid not in self._history:
            self._history[sid] = []
        history = self._history[sid]
        history.append(event)
        if len(history) > self._max_history:
            self._history[sid] = history[-self._max_history:]

        # 广播
        queues = self._subscribers.get(sid, [])
        dead: list[asyncio.Queue[AgentEvent]] = []
        for q in queues:
            try:
                q.put_nowait(event)
            except asyncio.QueueFull:
                dead.append(q)
        for q in dead:
            try:
                queues.remove(q)
            except ValueError:
                pass

    async def subscribe(
        self, session_id: str, max_queue: int = 256
    ) -> AsyncIterator[AgentEvent]:
        """订阅 session 事件流."""
        q: asyncio.Queue[AgentEvent] = asyncio.Queue(maxsize=max_queue)

        if session_id not in self._subscribers:
            self._subscribers[session_id] = []
        self._subscribers[session_id].append(q)

        try:
            while True:
                event = await q.get()
                yield event
        finally:
            try:
                self._subscribers[session_id].remove(q)
            except (KeyError, ValueError):
                pass

    def history(self, session_id: str) -> list[AgentEvent]:
        """获取 session 的历史事件 (Worklog)."""
        return list(self._history.get(session_id, []))

    def clear_history(self, session_id: str) -> None:
        """清空 session 历史."""
        self._history.pop(session_id, None)

    def active_sessions(self) -> list[str]:
        """返回有活跃订阅者的 session 列表."""
        return [
            sid
            for sid, qs in self._subscribers.items()
            if qs
        ]


# 全局单例
event_hub = EventHub()
