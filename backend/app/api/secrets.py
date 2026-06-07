"""密钥管理 API / Secrets management endpoints.

仅暴露密钥名称，不返回密钥值。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.secrets_service import secrets_service

router = APIRouter()


class CreateSecretRequest(BaseModel):
    name: str
    value: str
    scope: str = "org"  # org / user / repo
    repo_name: str | None = None


class UpdateSecretRequest(BaseModel):
    value: str


@router.get("/")
async def list_secrets(scope: str | None = None, repo_name: str | None = None):
    """列出密钥（仅名称，不含值）."""
    secrets = secrets_service.list_secrets(scope=scope, repo_name=repo_name)
    return {"secrets": secrets, "total": len(secrets)}


@router.post("/")
async def create_secret(req: CreateSecretRequest):
    """创建密钥."""
    secret = secrets_service.create_secret(
        name=req.name,
        value=req.value,
        scope=req.scope,
        repo_name=req.repo_name,
    )
    return secret.to_dict()


@router.delete("/{secret_id}")
async def delete_secret(secret_id: str):
    """删除密钥."""
    if not secrets_service.delete_secret(secret_id):
        raise HTTPException(status_code=404, detail="密钥不存在")
    return {"status": "deleted", "id": secret_id}


@router.put("/{secret_id}")
async def update_secret(secret_id: str, req: UpdateSecretRequest):
    """更新密钥值."""
    if not secrets_service.update_secret(secret_id, req.value):
        raise HTTPException(status_code=404, detail="密钥不存在")
    return {"status": "updated", "id": secret_id}
