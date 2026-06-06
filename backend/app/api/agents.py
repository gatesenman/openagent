"""Agent API / Agent endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_agents():
    return {"agents": [], "total": 0}
