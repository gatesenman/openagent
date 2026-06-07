"""Worklog API."""

from fastapi import APIRouter

from app.services.worklog_service import worklog_service

router = APIRouter()


@router.get("/{session_id}")
async def get_timeline(session_id: str, category: str = "", limit: int = 100):
    """获取会话时间线."""
    return {
        "timeline": worklog_service.get_timeline(session_id, category=category, limit=limit),
    }


@router.post("/{session_id}")
async def log_entry(session_id: str, data: dict):
    """记录 Worklog 条目."""
    entry = worklog_service.log(
        session_id=session_id,
        category=data.get("category", "tool_call"),
        title=data.get("title", ""),
        detail=data.get("detail", ""),
        duration_ms=data.get("duration_ms", 0),
        metadata=data.get("metadata"),
    )
    return {"id": entry.id}


@router.post("/{session_id}/annotate")
async def annotate_entry(session_id: str, data: dict):
    """添加注释."""
    ok = worklog_service.annotate(
        data.get("entry_id", ""), session_id, data.get("text", "")
    )
    return {"ok": ok}


@router.get("/{session_id}/summary")
async def worklog_summary(session_id: str):
    """获取摘要统计."""
    return worklog_service.get_summary(session_id)


@router.get("/{session_id}/milestones")
async def get_milestones(session_id: str):
    """获取里程碑."""
    return {"milestones": worklog_service.extract_milestones(session_id)}


@router.post("/{session_id}/replay/start")
async def start_replay(session_id: str, data: dict | None = None):
    """开始回放."""
    speed = (data or {}).get("speed", 1.0)
    worklog_service.start_replay(session_id, speed)
    return {"status": "replaying"}


@router.get("/{session_id}/replay/next")
async def replay_next(session_id: str):
    """获取下一个回放事件."""
    event = worklog_service.replay_next(session_id)
    return event or {"status": "done"}


@router.post("/{session_id}/replay/stop")
async def stop_replay(session_id: str):
    """停止回放."""
    worklog_service.stop_replay(session_id)
    return {"status": "stopped"}
