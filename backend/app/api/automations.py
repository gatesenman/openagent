"""自动化 API / Automation endpoints.

自动化规则 + 定时任务 + Webhook 接收。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.automation_service import automation_service

router = APIRouter()


class RuleCreate(BaseModel):
    name: str
    description: str = ""
    trigger_type: str = "webhook"
    trigger_config: dict = {}
    conditions: list[dict] = []
    actions: list[dict] = []
    playbook_id: str | None = None


class ScheduleCreate(BaseModel):
    name: str
    cron: str = "0 9 * * 1-5"
    timezone: str = "Asia/Shanghai"
    prompt: str = ""
    playbook_id: str | None = None


class WebhookPayload(BaseModel):
    event_type: str
    payload: dict = {}


# --- 自动化规则 ---

@router.get("/rules")
async def list_rules():
    """列出所有自动化规则."""
    return [r.to_dict() for r in automation_service.list_rules()]


@router.post("/rules")
async def create_rule(data: RuleCreate):
    """创建自动化规则."""
    rule = automation_service.create_rule(**data.model_dump())
    return rule.to_dict()


@router.delete("/rules/{rule_id}")
async def delete_rule(rule_id: str):
    """删除自动化规则."""
    if not automation_service.delete_rule(rule_id):
        raise HTTPException(status_code=404, detail="规则未找到")
    return {"deleted": True}


# --- 定时任务 ---

@router.get("/schedules")
async def list_schedules():
    """列出所有定时任务."""
    return [s.to_dict() for s in automation_service.list_schedules()]


@router.post("/schedules")
async def create_schedule(data: ScheduleCreate):
    """创建定时任务."""
    schedule = automation_service.create_schedule(**data.model_dump())
    return schedule.to_dict()


@router.delete("/schedules/{schedule_id}")
async def delete_schedule(schedule_id: str):
    """删除定时任务."""
    if not automation_service.delete_schedule(schedule_id):
        raise HTTPException(status_code=404, detail="任务未找到")
    return {"deleted": True}


# --- Webhook ---

@router.post("/webhook")
async def receive_webhook(data: WebhookPayload):
    """接收外部 Webhook 事件（GitHub/GitLab等）."""
    result = await automation_service.handle_webhook(data.event_type, data.payload)
    return result


@router.get("/webhook/history")
async def webhook_history(limit: int = 50):
    """查看 Webhook 接收历史."""
    return automation_service.get_webhook_history(limit)
