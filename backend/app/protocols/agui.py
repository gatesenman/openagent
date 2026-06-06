"""AG-UI 事件标准 / AG-UI Event Standard.

定义 Agent-UI 之间的标准事件类型。
参考: https://docs.ag-ui.com/concepts/events

所有 Agent 操作都通过 AG-UI 事件流推送到前端，
前端通过 SSE 或 WebSocket 接收实时更新。
"""

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AGUIEventType(str, Enum):
    """AG-UI 标准事件类型（16种）."""

    # === 运行生命周期 ===
    RUN_STARTED = "RUN_STARTED"          # Agent 开始执行
    RUN_FINISHED = "RUN_FINISHED"        # Agent 执行完成
    RUN_ERROR = "RUN_ERROR"              # Agent 执行出错

    # === 步骤生命周期 ===
    STEP_STARTED = "STEP_STARTED"        # 步骤开始（Think/Act/Observe/Reflect）
    STEP_FINISHED = "STEP_FINISHED"      # 步骤完成

    # === 文本消息流 ===
    TEXT_MESSAGE_START = "TEXT_MESSAGE_START"      # 文本消息开始
    TEXT_MESSAGE_CONTENT = "TEXT_MESSAGE_CONTENT"  # 文本消息内容（增量）
    TEXT_MESSAGE_END = "TEXT_MESSAGE_END"          # 文本消息结束

    # === 工具调用流 ===
    TOOL_CALL_START = "TOOL_CALL_START"        # 工具调用开始
    TOOL_CALL_ARGS = "TOOL_CALL_ARGS"          # 工具调用参数（增量）
    TOOL_CALL_END = "TOOL_CALL_END"            # 工具调用结束

    # === 状态同步 ===
    STATE_SNAPSHOT = "STATE_SNAPSHOT"    # 完整状态快照
    STATE_DELTA = "STATE_DELTA"         # 增量状态更新

    # === 自定义扩展 ===
    CUSTOM = "CUSTOM"                    # 自定义事件

    # === OpenAgent 扩展事件 ===
    PLAN_UPDATE = "PLAN_UPDATE"          # 计划更新
    SANDBOX_STATUS = "SANDBOX_STATUS"    # 沙箱状态变更


@dataclass
class AGUIEvent:
    """AG-UI 标准事件.

    每个事件包含:
    - type: 事件类型
    - timestamp: Unix 毫秒时间戳
    - data: 事件数据
    """

    type: AGUIEventType
    data: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: int = field(default_factory=lambda: int(time.time() * 1000))

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "type": self.type.value,
            "timestamp": self.timestamp,
            "data": self.data,
        }

    def to_sse(self) -> str:
        """转换为 SSE 格式字符串."""
        import json
        data = json.dumps(self.to_dict(), ensure_ascii=False)
        return f"event: {self.type.value}\ndata: {data}\n\n"


class AGUIEventBuilder:
    """AG-UI 事件构建器.

    提供便捷方法创建各类标准事件。
    """

    @staticmethod
    def run_started(session_id: str, model: str = "") -> AGUIEvent:
        return AGUIEvent(
            type=AGUIEventType.RUN_STARTED,
            data={"session_id": session_id, "model": model},
        )

    @staticmethod
    def run_finished(session_id: str, reason: str = "completed") -> AGUIEvent:
        return AGUIEvent(
            type=AGUIEventType.RUN_FINISHED,
            data={"session_id": session_id, "reason": reason},
        )

    @staticmethod
    def run_error(session_id: str, error: str) -> AGUIEvent:
        return AGUIEvent(
            type=AGUIEventType.RUN_ERROR,
            data={"session_id": session_id, "error": error},
        )

    @staticmethod
    def step_started(step: str, iteration: int = 0) -> AGUIEvent:
        return AGUIEvent(
            type=AGUIEventType.STEP_STARTED,
            data={"step": step, "iteration": iteration},
        )

    @staticmethod
    def step_finished(step: str, duration_ms: int = 0) -> AGUIEvent:
        return AGUIEvent(
            type=AGUIEventType.STEP_FINISHED,
            data={"step": step, "duration_ms": duration_ms},
        )

    @staticmethod
    def text_message_start(message_id: str, role: str = "assistant") -> AGUIEvent:
        return AGUIEvent(
            type=AGUIEventType.TEXT_MESSAGE_START,
            data={"message_id": message_id, "role": role},
        )

    @staticmethod
    def text_message_content(message_id: str, delta: str) -> AGUIEvent:
        return AGUIEvent(
            type=AGUIEventType.TEXT_MESSAGE_CONTENT,
            data={"message_id": message_id, "delta": delta},
        )

    @staticmethod
    def text_message_end(message_id: str) -> AGUIEvent:
        return AGUIEvent(
            type=AGUIEventType.TEXT_MESSAGE_END,
            data={"message_id": message_id},
        )

    @staticmethod
    def tool_call_start(
        tool_call_id: str, tool_name: str, parent_message_id: str = ""
    ) -> AGUIEvent:
        return AGUIEvent(
            type=AGUIEventType.TOOL_CALL_START,
            data={
                "tool_call_id": tool_call_id,
                "tool_name": tool_name,
                "parent_message_id": parent_message_id,
            },
        )

    @staticmethod
    def tool_call_args(tool_call_id: str, delta: str) -> AGUIEvent:
        return AGUIEvent(
            type=AGUIEventType.TOOL_CALL_ARGS,
            data={"tool_call_id": tool_call_id, "delta": delta},
        )

    @staticmethod
    def tool_call_end(tool_call_id: str, result: str = "") -> AGUIEvent:
        return AGUIEvent(
            type=AGUIEventType.TOOL_CALL_END,
            data={"tool_call_id": tool_call_id, "result": result},
        )

    @staticmethod
    def state_snapshot(state: dict) -> AGUIEvent:
        return AGUIEvent(
            type=AGUIEventType.STATE_SNAPSHOT,
            data={"snapshot": state},
        )

    @staticmethod
    def state_delta(operations: list[dict]) -> AGUIEvent:
        """JSON Patch 格式的增量更新."""
        return AGUIEvent(
            type=AGUIEventType.STATE_DELTA,
            data={"delta": operations},
        )

    @staticmethod
    def plan_update(
        steps: list[dict], current_step: int = 0, status: str = "running"
    ) -> AGUIEvent:
        return AGUIEvent(
            type=AGUIEventType.PLAN_UPDATE,
            data={
                "steps": steps,
                "current_step": current_step,
                "status": status,
            },
        )

    @staticmethod
    def sandbox_status(
        session_id: str, status: str, sandbox_type: str = "docker"
    ) -> AGUIEvent:
        return AGUIEvent(
            type=AGUIEventType.SANDBOX_STATUS,
            data={
                "session_id": session_id,
                "status": status,
                "sandbox_type": sandbox_type,
            },
        )
