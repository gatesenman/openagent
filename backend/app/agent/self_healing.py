"""Agent 自我纠错机制 / Self-Healing mechanism.

检测 Agent 的错误模式并自动切换策略：
- 连续 N 次相同错误 → 切换策略
- 死循环检测 → 中断并求助
- 代码改坏 → 自动 revert
- 检查点恢复 → 回到已知好状态
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ErrorPattern(str, Enum):
    REPEATED_FAILURE = "repeated_failure"      # 连续相同错误
    INFINITE_LOOP = "infinite_loop"            # 死循环
    REGRESSION = "regression"                  # 回归（之前通过的测试现在失败）
    RESOURCE_EXHAUSTION = "resource_exhaustion" # 资源耗尽
    STUCK = "stuck"                            # 无进展


class RecoveryAction(str, Enum):
    SWITCH_STRATEGY = "switch_strategy"  # 切换策略
    REVERT = "revert"                    # 回退代码
    CHECKPOINT = "checkpoint"            # 恢复到检查点
    ESCALATE = "escalate"                # 升级给用户
    REDUCE_SCOPE = "reduce_scope"        # 缩小范围


@dataclass
class ErrorRecord:
    """错误记录."""
    error_type: str
    message: str
    tool_name: str = ""
    timestamp: float = field(default_factory=time.time)
    context: str = ""


@dataclass
class Checkpoint:
    """检查点."""
    id: str
    timestamp: float
    description: str
    state: dict = field(default_factory=dict)


class SelfHealingEngine:
    """自我纠错引擎.

    监控 Agent 的执行过程，检测异常模式并自动恢复。
    """

    def __init__(self):
        self._error_history: list[ErrorRecord] = []
        self._action_history: list[str] = []
        self._checkpoints: list[Checkpoint] = []
        self._consecutive_errors = 0
        self._max_consecutive_errors = 3
        self._max_loop_detection = 5
        self._strategy_switches = 0

    def record_error(self, error: ErrorRecord) -> RecoveryAction | None:
        """记录错误并判断是否需要自动恢复."""
        self._error_history.append(error)
        self._consecutive_errors += 1

        # 检测各种错误模式
        pattern = self._detect_pattern()
        if pattern:
            action = self._recommend_action(pattern)
            logger.warning(
                "检测到错误模式 [%s]，建议 [%s]: %s",
                pattern.value, action.value, error.message,
            )
            return action

        return None

    def record_success(self):
        """记录成功操作，重置连续错误计数."""
        self._consecutive_errors = 0

    def record_action(self, action: str):
        """记录 Agent 动作（用于死循环检测）."""
        self._action_history.append(action)
        if len(self._action_history) > 100:
            self._action_history = self._action_history[-100:]

    def create_checkpoint(self, description: str, state: dict) -> Checkpoint:
        """创建检查点."""
        import uuid
        cp = Checkpoint(
            id=str(uuid.uuid4()),
            timestamp=time.time(),
            description=description,
            state=state,
        )
        self._checkpoints.append(cp)
        logger.info("检查点已创建: %s", description)
        return cp

    def get_latest_checkpoint(self) -> Checkpoint | None:
        """获取最近的检查点."""
        return self._checkpoints[-1] if self._checkpoints else None

    def _detect_pattern(self) -> ErrorPattern | None:
        """检测错误模式."""
        # 1. 连续相同错误
        if self._consecutive_errors >= self._max_consecutive_errors:
            recent = self._error_history[-self._max_consecutive_errors:]
            error_types = {e.error_type for e in recent}
            if len(error_types) == 1:
                return ErrorPattern.REPEATED_FAILURE

        # 2. 死循环检测（最近 N 个动作重复）
        if len(self._action_history) >= self._max_loop_detection * 2:
            recent = self._action_history[-self._max_loop_detection:]
            previous = self._action_history[
                -self._max_loop_detection * 2:-self._max_loop_detection
            ]
            if recent == previous:
                return ErrorPattern.INFINITE_LOOP

        # 3. 无进展检测
        if self._consecutive_errors >= 5:
            return ErrorPattern.STUCK

        return None

    def _recommend_action(self, pattern: ErrorPattern) -> RecoveryAction:
        """根据错误模式推荐恢复动作."""
        action_map = {
            ErrorPattern.REPEATED_FAILURE: RecoveryAction.SWITCH_STRATEGY,
            ErrorPattern.INFINITE_LOOP: RecoveryAction.ESCALATE,
            ErrorPattern.REGRESSION: RecoveryAction.REVERT,
            ErrorPattern.RESOURCE_EXHAUSTION: RecoveryAction.REDUCE_SCOPE,
            ErrorPattern.STUCK: RecoveryAction.ESCALATE,
        }
        action = action_map.get(pattern, RecoveryAction.ESCALATE)

        # 如果已经切换过策略多次，升级给用户
        if (action == RecoveryAction.SWITCH_STRATEGY
            and self._strategy_switches >= 2):
            action = RecoveryAction.ESCALATE

        if action == RecoveryAction.SWITCH_STRATEGY:
            self._strategy_switches += 1

        return action

    def get_stats(self) -> dict:
        """获取自愈统计."""
        return {
            "total_errors": len(self._error_history),
            "consecutive_errors": self._consecutive_errors,
            "strategy_switches": self._strategy_switches,
            "checkpoints": len(self._checkpoints),
            "recent_errors": [
                {"type": e.error_type, "message": e.message[:100]}
                for e in self._error_history[-5:]
            ],
        }

    def reset(self):
        """重置状态."""
        self._error_history.clear()
        self._action_history.clear()
        self._consecutive_errors = 0
        self._strategy_switches = 0
