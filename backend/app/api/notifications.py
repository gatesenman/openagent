"""通知 API / Notifications API."""

from fastapi import APIRouter

from app.services.notification_service import notification_service

router = APIRouter()


@router.get("/")
async def list_notifications(user_id: str = "", unread_only: bool = False):
    """获取通知列表."""
    return {
        "notifications": notification_service.get_notifications(user_id, unread_only),
    }


@router.post("/{notification_id}/read")
async def mark_read(notification_id: str):
    """标记已读."""
    notification_service.mark_read(notification_id)
    return {"ok": True}


@router.post("/read-all")
async def mark_all_read(data: dict):
    """标记所有已读."""
    count = notification_service.mark_all_read(data.get("user_id", ""))
    return {"marked": count}


@router.get("/channels")
async def list_channels():
    """获取通知渠道配置."""
    return {"channels": notification_service.get_channel_configs()}
