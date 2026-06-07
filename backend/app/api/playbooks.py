"""Playbook API — 可复用的 Agent 任务模板.

接口:
  GET    /api/playbooks           Playbook 列表
  POST   /api/playbooks           创建 Playbook
  GET    /api/playbooks/{id}      获取 Playbook 详情
  DELETE /api/playbooks/{id}      删除 Playbook
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.playbook.playbook_manager import playbook_manager

router = APIRouter()


class PlaybookCreate(BaseModel):
    name: str
    description: str = ""
    category: str = "general"
    system_prompt: str = ""
    steps: list[dict] = []
    tags: list[str] = []
    variables: list[str] = []


@router.get("/")
async def list_playbooks(
    scope: str | None = None,
    category: str | None = None,
):
    """获取 Playbook 列表."""
    playbooks = playbook_manager.list_playbooks(scope=scope, category=category)
    return {
        "playbooks": [p.to_dict() for p in playbooks],
        "total": len(playbooks),
    }


@router.post("/")
async def create_playbook(data: PlaybookCreate):
    """创建自定义 Playbook."""
    playbook = playbook_manager.create_playbook(data.model_dump())
    return playbook.to_dict()


@router.get("/{playbook_id}")
async def get_playbook(playbook_id: str):
    """获取 Playbook 详情（含完整系统提示词）."""
    playbook = playbook_manager.get_playbook(playbook_id)
    if not playbook:
        raise HTTPException(status_code=404, detail="Playbook 不存在")
    return {
        **playbook.to_dict(),
        "system_prompt": playbook.system_prompt,
        "full_prompt": playbook.to_full_prompt(),
    }


@router.delete("/{playbook_id}")
async def delete_playbook(playbook_id: str):
    """删除 Playbook."""
    try:
        ok = playbook_manager.delete_playbook(playbook_id)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    if not ok:
        raise HTTPException(status_code=404, detail="Playbook 不存在")
    return {"message": "已删除"}
