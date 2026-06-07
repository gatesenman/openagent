"""批量会话 API."""

from fastapi import APIRouter

from app.services.batch_session_service import batch_session_service

router = APIRouter()


@router.post("/")
async def create_batch(data: dict):
    batch = batch_session_service.create_batch(
        parent_session_id=data.get("parent_session_id", ""),
        title=data.get("title", ""),
        subtask_prompts=data.get("subtasks", []),
        merge_strategy=data.get("merge_strategy", "auto"),
    )
    return {"id": batch.id, "subtask_count": len(batch.subtasks)}


@router.post("/{batch_id}/start")
async def start_batch(batch_id: str):
    batch = batch_session_service.start_batch(batch_id)
    if not batch:
        return {"error": "not found"}
    return {"status": batch.status.value}


@router.get("/{batch_id}")
async def get_batch(batch_id: str):
    result = batch_session_service.get_batch(batch_id)
    return result or {"error": "not found"}


@router.put("/{batch_id}/subtask/{subtask_id}")
async def update_subtask(batch_id: str, subtask_id: str, data: dict):
    return {"ok": batch_session_service.update_subtask(
        batch_id, subtask_id, data.get("status", ""), data.get("result", "")
    )}


@router.get("/")
async def list_batches(parent_session_id: str = ""):
    return {"batches": batch_session_service.list_batches(parent_session_id)}
