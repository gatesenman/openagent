"""自动化/Webhook 服务 / Automation & Webhook service.

支持:
- 定时任务 (Schedules)
- Webhook 触发 (Git push/PR/Issue 事件)
- 自动化规则 (基于条件的 Agent 会话创建)
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class TriggerType(str, Enum):
    """触发器类型."""
    WEBHOOK = "webhook"
    SCHEDULE = "schedule"
    EVENT = "event"
    MANUAL = "manual"


class WebhookEvent(str, Enum):
    """Webhook 事件类型."""
    PUSH = "push"
    PULL_REQUEST = "pull_request"
    ISSUE = "issue"
    COMMENT = "comment"
    RELEASE = "release"
    WORKFLOW_RUN = "workflow_run"


@dataclass
class AutomationRule:
    """自动化规则."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    enabled: bool = True
    trigger_type: TriggerType = TriggerType.WEBHOOK
    trigger_config: dict = field(default_factory=dict)
    conditions: list[dict] = field(default_factory=list)
    actions: list[dict] = field(default_factory=list)
    playbook_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "trigger_type": self.trigger_type.value if hasattr(self.trigger_type, 'value') else str(self.trigger_type),
            "trigger_config": self.trigger_config,
            "conditions": self.conditions,
            "actions": self.actions,
            "playbook_id": self.playbook_id,
            "created_at": self.created_at,
        }

    def matches(self, event: dict) -> bool:
        """检查事件是否匹配规则条件."""
        if not self.enabled:
            return False
        for cond in self.conditions:
            field_name = cond.get("field", "")
            operator = cond.get("operator", "eq")
            value = cond.get("value")
            actual = event.get(field_name)
            if operator == "eq" and actual != value:
                return False
            if operator == "contains" and value not in str(actual):
                return False
            if operator == "regex":
                import re
                if not re.search(str(value), str(actual)):
                    return False
        return True


@dataclass
class Schedule:
    """定时任务."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    cron: str = "0 9 * * 1-5"  # 默认工作日 9:00
    timezone: str = "Asia/Shanghai"
    enabled: bool = True
    prompt: str = ""
    playbook_id: str | None = None
    last_run: str | None = None
    next_run: str | None = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "cron": self.cron,
            "timezone": self.timezone,
            "enabled": self.enabled,
            "prompt": self.prompt,
            "playbook_id": self.playbook_id,
            "last_run": self.last_run,
            "next_run": self.next_run,
            "created_at": self.created_at,
        }


class AutomationService:
    """自动化服务.

    管理自动化规则和定时任务。
    Phase 1: 内存存储 + Webhook 端点
    Phase 2: 持久化 + APScheduler + 分布式锁
    """

    def __init__(self) -> None:
        self._rules: dict[str, AutomationRule] = {}
        self._schedules: dict[str, Schedule] = {}
        self._webhook_history: list[dict] = []
        self._init_defaults()

    def _init_defaults(self) -> None:
        """创建默认自动化规则."""
        # PR 自动审查
        pr_review = AutomationRule(
            name="PR 自动审查",
            description="新 PR 创建时自动触发代码审查",
            trigger_type=TriggerType.WEBHOOK,
            trigger_config={"event": "pull_request"},
            conditions=[{"field": "action", "operator": "eq", "value": "opened"}],
            actions=[{"type": "create_session", "playbook": "code-review"}],
            playbook_id="code-review",
        )
        self._rules[pr_review.id] = pr_review

        # Issue 自动分析
        issue_analyze = AutomationRule(
            name="Issue Bug 分析",
            description="新 Bug Issue 创建时自动分析",
            trigger_type=TriggerType.WEBHOOK,
            trigger_config={"event": "issue"},
            conditions=[
                {"field": "action", "operator": "eq", "value": "opened"},
                {"field": "labels", "operator": "contains", "value": "bug"},
            ],
            actions=[{"type": "create_session", "playbook": "bug-fix"}],
            playbook_id="bug-fix",
        )
        self._rules[issue_analyze.id] = issue_analyze

    # --- 自动化规则 CRUD ---

    def list_rules(self) -> list[AutomationRule]:
        return list(self._rules.values())

    def get_rule(self, rule_id: str) -> AutomationRule | None:
        return self._rules.get(rule_id)

    def create_rule(self, **kwargs: Any) -> AutomationRule:
        rule = AutomationRule(**kwargs)
        self._rules[rule.id] = rule
        logger.info("自动化规则已创建: %s", rule.name)
        return rule

    def update_rule(self, rule_id: str, **kwargs: Any) -> AutomationRule | None:
        rule = self._rules.get(rule_id)
        if not rule:
            return None
        for k, v in kwargs.items():
            if hasattr(rule, k):
                setattr(rule, k, v)
        return rule

    def delete_rule(self, rule_id: str) -> bool:
        return self._rules.pop(rule_id, None) is not None

    # --- 定时任务 CRUD ---

    def list_schedules(self) -> list[Schedule]:
        return list(self._schedules.values())

    def create_schedule(self, **kwargs: Any) -> Schedule:
        schedule = Schedule(**kwargs)
        self._schedules[schedule.id] = schedule
        logger.info("定时任务已创建: %s (%s)", schedule.name, schedule.cron)
        return schedule

    def delete_schedule(self, schedule_id: str) -> bool:
        return self._schedules.pop(schedule_id, None) is not None

    # --- Webhook 处理 ---

    async def handle_webhook(self, event_type: str, payload: dict) -> dict:
        """处理传入的 Webhook 事件."""
        self._webhook_history.append({
            "event_type": event_type,
            "payload_summary": str(payload)[:500],
            "received_at": datetime.utcnow().isoformat(),
        })

        triggered = []
        for rule in self._rules.values():
            if rule.trigger_config.get("event") == event_type:
                if rule.matches(payload):
                    triggered.append(rule.to_dict())
                    logger.info("规则匹配: %s -> %s", event_type, rule.name)

        return {
            "event_type": event_type,
            "rules_matched": len(triggered),
            "triggered_rules": triggered,
        }

    def get_webhook_history(self, limit: int = 50) -> list[dict]:
        return self._webhook_history[-limit:]


automation_service = AutomationService()
