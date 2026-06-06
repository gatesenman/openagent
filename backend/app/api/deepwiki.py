"""DeepWiki API / DeepWiki endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def deepwiki_status():
    return {"status": "ready", "indexed_repos": 0}
