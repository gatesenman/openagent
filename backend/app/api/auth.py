"""认证 API / Authentication endpoints."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from app.core.auth import (
    Role,
    create_access_token,
    user_store,
)

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    org_id: str = ""


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str
    role: str


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    """用户登录, 返回 JWT Token."""
    user = user_store.authenticate(req.username, req.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    token = create_access_token(
        user_id=user.id,
        org_id=user.org_id,
        role=user.role,
    )
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        role=user.role.value,
    )


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest):
    """用户注册."""
    try:
        user = user_store.create_user(
            username=req.username,
            email=req.email,
            password=req.password,
            org_id=req.org_id,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )

    token = create_access_token(
        user_id=user.id,
        org_id=user.org_id,
        role=user.role,
    )
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        username=user.username,
        role=user.role.value,
    )


@router.get("/me")
async def get_me():
    """获取当前用户信息 (开发模式无需 Token)."""
    return {
        "user_id": "dev-user",
        "username": "admin",
        "role": "admin",
        "org_id": "",
    }
