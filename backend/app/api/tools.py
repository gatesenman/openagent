"""工具 API / Tool endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_tools():
    return {"tools": [], "total": 0}
