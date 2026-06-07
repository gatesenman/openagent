"""API Keys / Service Users 管理 API."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.apikeys_service import apikeys_service

router = APIRouter()


class CreateServiceUserRequest(BaseModel):
    name: str
    description: str = ""
    permissions: list[str] | None = None


@router.get("/")
async def list_service_users():
    """列出 Service Users."""
    users = apikeys_service.list_service_users()
    return {"service_users": users, "total": len(users)}


@router.post("/")
async def create_service_user(req: CreateServiceUserRequest):
    """创建 Service User 并生成 API Key.

    注意：API Key 仅在创建时返回一次。
    """
    user, raw_key = apikeys_service.create_service_user(
        name=req.name,
        description=req.description,
        permissions=req.permissions,
    )
    result = user.to_dict()
    result["api_key"] = raw_key  # 仅此次返回
    return result


@router.delete("/{user_id}")
async def delete_service_user(user_id: str):
    """删除 Service User."""
    if not apikeys_service.delete_service_user(user_id):
        raise HTTPException(status_code=404, detail="Service User 不存在")
    return {"status": "deleted", "id": user_id}


@router.post("/{user_id}/toggle")
async def toggle_service_user(user_id: str):
    """启用/禁用 Service User."""
    user = apikeys_service.toggle_service_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Service User 不存在")
    return user.to_dict()
