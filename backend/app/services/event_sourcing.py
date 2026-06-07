"""事件溯源服务 / Event Sourcing service.

Agent 的每个动作都是不可篡改的事件：
- 支持时间旅行（回放任意时间点的状态）
- 因果追踪（一个操作导致了哪些后续事件）
- 会话回放（像看视频一样回放 Agent 操作）
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    # Agent 动作事件
    AGENT_THINK = "agent.think"
    AGENT_ACT = "agent.act"
    AGENT_OBSERVE = "agent.observe"
    AGENT_REFLECT = "agent.reflect"
    AGENT_PLAN = "agent.plan"
    # 工具执行事件
    TOOL_CALL = "tool.call"
    TOOL_RESULT = "tool.result"
    TOOL_ERROR = "tool.error"
    # 沙箱事件
    SANDBOX_CREATE = "sandbox.create"
    SANDBOX_EXEC = "sandbox.exec"
    SANDBOX_FILE_WRITE = "sandbox.file_write"
    SANDBOX_FILE_READ = "sandbox.file_read"
    SANDBOX_DESTROY = "sandbox.destroy"
    # Git 事件
    GIT_CLONE = "git.clone"
    GIT_COMMIT = "git.commit"
    GIT_PUSH = "git.push"
    GIT_PR = "git.pr"
    # 会话事件
    SESSION_CREATE = "session.create"
    SESSION_PAUSE = "session.pause"
    SESSION_RESUME = "session.resume"
    SESSION_COMPLETE = "session.complete"
    SESSION_FORK = "session.fork"
    # 用户事件
    USER_MESSAGE = "user.message"
    USER_APPROVE = "user.approve"
    USER_REJECT = "user.reject"
    USER_FEEDBACK = "user.feedback"


@dataclass
class Event:
    """不可变事件."""
    id: str
    session_id: str
    event_type: EventType
    timestamp: float
    data: dict = field(default_factory=dict)
    parent_event_id: str | None = None  # 因果链
    actor: str = "agent"  # agent / user / system
    sequence_number: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "session_id": self.session_id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "data": self.data,
            "parent_event_id": self.parent_event_id,
            "actor": self.actor,
            "sequence_number": self.sequence_number,
        }


class EventStore:
    """事件存储.

    Phase 1: 内存存储。
    Phase 2: PostgreSQL + 分区表 + 索引。
    """

    def __init__(self):
        self._events: dict[str, list[Event]] = {}  # session_id → events
        self._sequence_counters: dict[str, int] = {}

    def append(
        self,
        session_id: str,
        event_type: EventType,
        data: dict | None = None,
        parent_event_id: str | None = None,
        actor: str = "agent",
    ) -> Event:
        """追加事件（不可修改已有事件）."""
        if session_id not in self._events:
            self._events[session_id] = []
            self._sequence_counters[session_id] = 0

        self._sequence_counters[session_id] += 1

        event = Event(
            id=str(uuid.uuid4()),
            session_id=session_id,
            event_type=event_type,
            timestamp=time.time(),
            data=data or {},
            parent_event_id=parent_event_id,
            actor=actor,
            sequence_number=self._sequence_counters[session_id],
        )
        self._events[session_id].append(event)
        return event

    def get_events(
        self,
        session_id: str,
        event_type: EventType | None = None,
        since: float | None = None,
        limit: int = 100,
    ) -> list[dict]:
        """查询事件."""
        events = self._events.get(session_id, [])
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if since:
            events = [e for e in events if e.timestamp >= since]
        return [e.to_dict() for e in events[-limit:]]

    def get_causal_chain(self, session_id: str, event_id: str) -> list[dict]:
        """获取事件的因果链（从根事件到当前事件）."""
        events = self._events.get(session_id, [])
        event_map = {e.id: e for e in events}

        chain: list[Event] = []
        current_id: str | None = event_id
        while current_id:
            event = event_map.get(current_id)
            if not event:
                break
            chain.append(event)
            current_id = event.parent_event_id

        chain.reverse()
        return [e.to_dict() for e in chain]

    def replay(
        self,
        session_id: str,
        from_sequence: int = 0,
        to_sequence: int | None = None,
    ) -> list[dict]:
        """回放事件（用于会话回放功能）."""
        events = self._events.get(session_id, [])
        filtered = [
            e for e in events
            if e.sequence_number >= from_sequence
            and (to_sequence is None or e.sequence_number <= to_sequence)
        ]
        return [e.to_dict() for e in filtered]

    def get_timeline(self, session_id: str) -> list[dict]:
        """获取会话时间线（Worklog 视图用）."""
        events = self._events.get(session_id, [])
        timeline = []
        for e in events:
            timeline.append({
                "id": e.id,
                "type": e.event_type.value,
                "timestamp": e.timestamp,
                "actor": e.actor,
                "summary": self._summarize_event(e),
                "sequence": e.sequence_number,
            })
        return timeline

    def _summarize_event(self, event: Event) -> str:
        """生成事件摘要."""
        summaries = {
            EventType.AGENT_THINK: "思考: " + event.data.get("thought", "")[:80],
            EventType.AGENT_ACT: "执行: " + event.data.get("tool", ""),
            EventType.TOOL_CALL: f"调用工具: {event.data.get('tool', '')}",
            EventType.TOOL_RESULT: "工具返回结果",
            EventType.SANDBOX_EXEC: f"执行命令: {event.data.get('command', '')[:60]}",
            EventType.GIT_COMMIT: f"提交: {event.data.get('message', '')[:60]}",
            EventType.USER_MESSAGE: f"用户: {event.data.get('content', '')[:60]}",
        }
        return summaries.get(event.event_type, event.event_type.value)

    def count_events(self, session_id: str) -> int:
        return len(self._events.get(session_id, []))


event_store = EventStore()
