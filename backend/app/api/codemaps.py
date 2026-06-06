"""CodeMap API / CodeMap endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def codemaps_status():
    return {"status": "ready", "indexed_repos": 0}
