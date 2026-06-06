"""会话 API / Session endpoints.

完整的会话生命周期管理 + SSE 实时事件流。
"""

import json
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session as DBSession

from app.core.database import get_db
from app.schemas.session import (
    EventResponse,
    MessageCreate,
    MessageResponse,
    SessionCreate,
    SessionList,
    SessionResponse,
    SessionUpdate,
)
from app.services.session_service import session_service

router = APIRouter()


@router.get("/", response_model=SessionList)
async def list_sessions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: str | None = None,
    db: DBSession = Depends(get_db),
):
    """获取会话列表."""
    sessions, total = session_service.list_sessions(db, skip, limit, status)
    return SessionList(
        sessions=[SessionResponse.model_validate(s) for s in sessions],
        total=total,
    )


@router.post("/", response_model=SessionResponse)
async def create_session(
    data: SessionCreate,
    db: DBSession = Depends(get_db),
):
    """创建新会话.

    创建会话的同时会启动一个沙箱虚拟环境。
    """
    session = await session_service.create_session(
        db=db,
        title=data.title,
        mode=data.mode,
        model=data.model,
        platform=data.platform,
        language=data.language,
        prompt=data.prompt,
    )
    return SessionResponse.model_validate(session)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: DBSession = Depends(get_db),
):
    """获取会话详情."""
    session = session_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return SessionResponse.model_validate(session)


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    data: SessionUpdate,
    db: DBSession = Depends(get_db),
):
    """更新会话."""
    session = session_service.update_session(
        db, session_id, **data.model_dump(exclude_none=True)
    )
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    return SessionResponse.model_validate(session)


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    db: DBSession = Depends(get_db),
):
    """删除会话（同时销毁沙箱虚拟环境）."""
    ok = await session_service.delete_session(db, session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="会话不存在")
    return {"message": "会话已删除"}


@router.post("/{session_id}/message")
async def send_message(
    session_id: str,
    data: MessageCreate,
    db: DBSession = Depends(get_db),
):
    """发送消息并触发 Agent 在沙箱中执行.

    返回 SSE 事件流，实时推送 Agent 的每一步操作。
    """
    session = session_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    async def event_stream():
        async for event in session_service.send_message(db, session_id, data.content):
            yield event.to_sse()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{session_id}/chat")
async def chat(
    session_id: str,
    data: MessageCreate,
    db: DBSession = Depends(get_db),
):
    """发送消息并返回 SSE 事件流（兼容前端 subscribeChatSSE）.

    与 /message 功能相同，额外路由方便前端调用。
    """
    session = session_service.get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    async def event_stream():
        async for event in session_service.send_message(db, session_id, data.content):
            yield event.to_sse()

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{session_id}/events")
async def get_events(
    session_id: str,
    db: DBSession = Depends(get_db),
):
    """获取会话事件历史（Worklog）."""
    events = session_service.get_events(db, session_id)
    return {
        "events": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "title": e.title,
                "content": e.content,
                "metadata": e.metadata_,
                "duration_ms": e.duration_ms,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in events
        ],
        "total": len(events),
    }


@router.get("/{session_id}/messages")
async def get_messages(
    session_id: str,
    db: DBSession = Depends(get_db),
):
    """获取消息历史."""
    messages = session_service.get_messages(db, session_id)
    return {
        "messages": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "tool_calls": m.tool_calls,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in messages
        ],
        "total": len(messages),
    }
