"""计费引擎 / Billing Engine.

ACU (Agent Compute Unit) 综合计费:
- 按会话大小分档 (XS-XL)
- LLM token 消耗
- 沙箱运行时长
- 存储用量

支持: 预付费包 + 超量按量 + 免费试用
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class SessionSize(str, Enum):
    XS = "xs"   # < 5 min, 简单问答
    S = "s"     # 5-15 min, 小型修改
    M = "m"     # 15-60 min, 中型功能
    L = "l"     # 1-4 hr, 大型开发
    XL = "xl"   # 4+ hr, 复杂项目


class PlanType(str, Enum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"


# ACU 定价 (每 ACU)
ACU_PRICES = {
    PlanType.FREE: 0.0,
    PlanType.PRO: 0.05,
    PlanType.TEAM: 0.04,
    PlanType.ENTERPRISE: 0.03,
}

# 会话大小 → ACU 消耗
SESSION_ACU = {
    SessionSize.XS: 1,
    SessionSize.S: 5,
    SessionSize.M: 20,
    SessionSize.L: 80,
    SessionSize.XL: 200,
}

# 计划额度
PLAN_QUOTAS = {
    PlanType.FREE: {"monthly_acu": 50, "max_sessions": 10, "max_sandboxes": 1},
    PlanType.PRO: {"monthly_acu": 500, "max_sessions": 100, "max_sandboxes": 5},
    PlanType.TEAM: {"monthly_acu": 2000, "max_sessions": 500, "max_sandboxes": 20},
    PlanType.ENTERPRISE: {"monthly_acu": 999999, "max_sessions": 999999, "max_sandboxes": 100},
}


@dataclass
class UsageRecord:
    """使用记录."""
    id: str = ""
    org_id: str = ""
    session_id: str = ""
    acu_consumed: float = 0.0
    token_input: int = 0
    token_output: int = 0
    sandbox_minutes: float = 0.0
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class OrgBilling:
    """组织计费信息."""
    org_id: str = ""
    plan: PlanType = PlanType.FREE
    monthly_acu_used: float = 0.0
    total_acu_used: float = 0.0
    billing_cycle_start: float = 0.0
    records: list[UsageRecord] = field(default_factory=list)


class BillingService:
    """计费引擎服务."""

    def __init__(self):
        self._billing: dict[str, OrgBilling] = {}

    def get_or_create_billing(self, org_id: str, plan: str = "free") -> OrgBilling:
        if org_id not in self._billing:
            self._billing[org_id] = OrgBilling(
                org_id=org_id,
                plan=PlanType(plan),
                billing_cycle_start=time.time(),
            )
        return self._billing[org_id]

    def classify_session_size(self, duration_minutes: float) -> SessionSize:
        """根据时长分类会话大小."""
        if duration_minutes < 5:
            return SessionSize.XS
        elif duration_minutes < 15:
            return SessionSize.S
        elif duration_minutes < 60:
            return SessionSize.M
        elif duration_minutes < 240:
            return SessionSize.L
        else:
            return SessionSize.XL

    def record_usage(
        self,
        org_id: str,
        session_id: str,
        duration_minutes: float = 0,
        token_input: int = 0,
        token_output: int = 0,
    ) -> UsageRecord:
        """记录使用量."""
        billing = self.get_or_create_billing(org_id)
        size = self.classify_session_size(duration_minutes)
        acu = SESSION_ACU[size]

        # LLM token 额外 ACU (每 1M token = 1 ACU)
        token_acu = (token_input + token_output) / 1_000_000
        total_acu = acu + token_acu

        record = UsageRecord(
            org_id=org_id,
            session_id=session_id,
            acu_consumed=total_acu,
            token_input=token_input,
            token_output=token_output,
            sandbox_minutes=duration_minutes,
        )
        billing.records.append(record)
        billing.monthly_acu_used += total_acu
        billing.total_acu_used += total_acu
        return record

    def get_usage_summary(self, org_id: str) -> dict:
        """获取用量摘要."""
        billing = self.get_or_create_billing(org_id)
        quota = PLAN_QUOTAS[billing.plan]
        return {
            "org_id": org_id,
            "plan": billing.plan.value,
            "monthly_acu_used": round(billing.monthly_acu_used, 2),
            "monthly_acu_limit": quota["monthly_acu"],
            "usage_percent": round(
                billing.monthly_acu_used / max(quota["monthly_acu"], 1) * 100, 1
            ),
            "total_sessions": len(billing.records),
            "estimated_cost": round(
                billing.monthly_acu_used * ACU_PRICES[billing.plan], 2
            ),
        }

    def check_quota(self, org_id: str) -> dict:
        """检查配额."""
        billing = self.get_or_create_billing(org_id)
        quota = PLAN_QUOTAS[billing.plan]
        remaining = quota["monthly_acu"] - billing.monthly_acu_used
        return {
            "within_quota": remaining > 0,
            "remaining_acu": round(max(0, remaining), 2),
            "plan": billing.plan.value,
        }

    def get_price_table(self) -> list[dict]:
        """获取价格表."""
        return [
            {
                "plan": plan.value,
                "acu_price": price,
                "monthly_acu": PLAN_QUOTAS[plan]["monthly_acu"],
                "max_sessions": PLAN_QUOTAS[plan]["max_sessions"],
                "max_sandboxes": PLAN_QUOTAS[plan]["max_sandboxes"],
            }
            for plan, price in ACU_PRICES.items()
        ]


billing_service = BillingService()
