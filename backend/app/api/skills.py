"""Skills 管理 API / Skills management endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.skills_service import skills_service

router = APIRouter()


class CreateSkillRequest(BaseModel):
    name: str
    description: str = ""
    content: str = ""
    path: str = ".agents/skills/SKILL.md"


class UpdateSkillRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    content: str | None = None


@router.get("/{repo_id}")
async def list_skills(repo_id: str):
    """列出仓库的 Skills."""
    skills = skills_service.list_skills(repo_id)
    return {"skills": skills, "total": len(skills)}


@router.post("/{repo_id}")
async def create_skill(repo_id: str, req: CreateSkillRequest):
    """创建 Skill."""
    skill = skills_service.create_skill(
        repo_id=repo_id,
        name=req.name,
        description=req.description,
        content=req.content,
        path=req.path,
    )
    return skill.to_dict()


@router.put("/{repo_id}/{skill_id}")
async def update_skill(repo_id: str, skill_id: str, req: UpdateSkillRequest):
    """更新 Skill."""
    skill = skills_service.update_skill(
        skill_id, name=req.name, description=req.description, content=req.content,
    )
    if not skill:
        raise HTTPException(status_code=404, detail="Skill 不存在")
    return skill.to_dict()


@router.delete("/{repo_id}/{skill_id}")
async def delete_skill(repo_id: str, skill_id: str):
    """删除 Skill."""
    if not skills_service.delete_skill(skill_id):
        raise HTTPException(status_code=404, detail="Skill 不存在")
    return {"status": "deleted", "id": skill_id}
