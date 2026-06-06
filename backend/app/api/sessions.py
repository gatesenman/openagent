"""会话 API / Session endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_sessions():
    return {"sessions": [], "total": 0}


@router.post("/")
async def create_session():
    return {"id": "placeholder", "status": "created"}
