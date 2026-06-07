"""Agent 记忆 API / Memory API."""

from fastapi import APIRouter

from app.services.memory_service import memory_service

router = APIRouter()


@router.get("/")
async def list_memories(
    session_id: str = "",
    tier: str = "",
    category: str = "",
    q: str = "",
):
    """查询记忆."""
    memories = memory_service.recall(
        query=q, session_id=session_id, tier=tier, category=category
    )
    return {
        "memories": [
            {
                "id": m.id,
                "content": m.content,
                "category": m.category,
                "tier": m.tier,
                "importance": round(m.effective_importance, 3),
                "tags": m.tags,
            }
            for m in memories
        ],
        "total": len(memories),
    }


@router.post("/")
async def create_memory(data: dict):
    """手动添加记忆."""
    entry = memory_service.remember(
        content=data.get("content", ""),
        session_id=data.get("session_id", ""),
        category=data.get("category", "fact"),
        importance=data.get("importance", 0.5),
        tier=data.get("tier", "working"),
        tags=data.get("tags"),
    )
    return {"id": entry.id, "tier": entry.tier, "category": entry.category}


@router.post("/{memory_id}/promote")
async def promote_memory(memory_id: str):
    """提升记忆层级."""
    mem = memory_service.promote(memory_id)
    if not mem:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="记忆不存在")
    return {"id": mem.id, "tier": mem.tier, "importance": mem.importance}


@router.delete("/{memory_id}")
async def forget_memory(memory_id: str):
    """删除记忆."""
    memory_service.forget(memory_id)
    return {"ok": True}


@router.get("/context/{session_id}")
async def get_session_context(session_id: str):
    """获取会话记忆上下文."""
    return {"context": memory_service.get_session_context(session_id)}


@router.get("/stats")
async def memory_stats():
    """记忆统计."""
    return memory_service.get_stats()


@router.post("/cleanup")
async def cleanup_memories():
    """清理衰减记忆."""
    removed = memory_service.cleanup()
    return {"removed": removed}
