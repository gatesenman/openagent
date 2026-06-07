"""事件流 API / Event streaming endpoints.

SSE + Worklog 查询, 参考 AG-UI 协议实现。
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.core.event_hub import AgentEvent, EventType, event_hub

router = APIRouter()


@router.get("/{session_id}/stream")
async def event_stream(session_id: str):
    """SSE 事件流 — 实时推送 Agent 操作事件."""

    async def generate():
        async for event in event_hub.subscribe(session_id):
            yield event.to_sse()

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{session_id}/worklog")
async def get_worklog(session_id: str, limit: int = 100):
    """获取 Session 的 Worklog (历史事件列表)."""
    events = event_hub.history(session_id)
    if limit:
        events = events[-limit:]
    return {
        "session_id": session_id,
        "total": len(events),
        "events": [e.to_dict() for e in events],
    }


@router.get("/{session_id}/worklog/summary")
async def worklog_summary(session_id: str):
    """Worklog 摘要统计."""
    events = event_hub.history(session_id)
    type_counts: dict[str, int] = {}
    for e in events:
        t = e.type.value
        type_counts[t] = type_counts.get(t, 0) + 1

    return {
        "session_id": session_id,
        "total_events": len(events),
        "by_type": type_counts,
        "first_event": events[0].to_dict() if events else None,
        "last_event": events[-1].to_dict() if events else None,
    }
