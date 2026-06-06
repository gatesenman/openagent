"""认证与授权 / Authentication & Authorization.

JWT Token 签发与验证 + OAuth 骨架。
参考 Devin 的 OAuth 2.0 / OIDC 集成方案。
"""

from __future__ import annotations

import hashlib
import hmac
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from app.core.config import settings

# ---------------------------------------------------------------------------
# JWT 简易实现 (避免引入 PyJWT 依赖, 后续可替换)
# ---------------------------------------------------------------------------

import base64
import json


class Role(str, Enum):
    """用户角色."""

    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


@dataclass
class TokenPayload:
    """JWT Payload."""

    sub: str  # user_id
    org_id: str = ""
    role: Role = Role.MEMBER
    exp: float = 0.0
    iat: float = 0.0


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(s: str) -> bytes:
    padding = 4 - len(s) % 4
    return base64.urlsafe_b64decode(s + "=" * padding)


def _sign(header_payload: str, secret: str) -> str:
    sig = hmac.new(
        secret.encode(), header_payload.encode(), hashlib.sha256
    ).digest()
    return _b64url_encode(sig)


def create_access_token(
    user_id: str,
    org_id: str = "",
    role: Role = Role.MEMBER,
    expires_minutes: int | None = None,
) -> str:
    """签发 JWT Access Token."""
    now = time.time()
    exp = now + (expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES) * 60

    header = _b64url_encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    payload = _b64url_encode(
        json.dumps(
            {
                "sub": user_id,
                "org_id": org_id,
                "role": role.value,
                "iat": now,
                "exp": exp,
            }
        ).encode()
    )

    header_payload = f"{header}.{payload}"
    signature = _sign(header_payload, settings.SECRET_KEY)
    return f"{header_payload}.{signature}"


def verify_token(token: str) -> Optional[TokenPayload]:
    """验证 JWT Token, 返回 payload 或 None."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        header_payload = f"{parts[0]}.{parts[1]}"
        expected_sig = _sign(header_payload, settings.SECRET_KEY)

        if not hmac.compare_digest(parts[2], expected_sig):
            return None

        payload_data = json.loads(_b64url_decode(parts[1]))

        if payload_data.get("exp", 0) < time.time():
            return None

        return TokenPayload(
            sub=payload_data["sub"],
            org_id=payload_data.get("org_id", ""),
            role=Role(payload_data.get("role", "member")),
            exp=payload_data["exp"],
            iat=payload_data.get("iat", 0),
        )
    except Exception:
        return None


# ---------------------------------------------------------------------------
# FastAPI 依赖注入
# ---------------------------------------------------------------------------

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer_scheme),
) -> TokenPayload:
    """从 Authorization header 提取并验证用户."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证凭据",
        )

    payload = verify_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token 无效或已过期",
        )
    return payload


async def require_admin(
    user: TokenPayload = Depends(get_current_user),
) -> TokenPayload:
    """要求管理员权限."""
    if user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return user


# ---------------------------------------------------------------------------
# 用户管理 (内存存储, Phase 2 切 PostgreSQL)
# ---------------------------------------------------------------------------


@dataclass
class User:
    """用户."""

    id: str
    username: str
    email: str
    password_hash: str
    org_id: str = ""
    role: Role = Role.MEMBER
    created_at: float = field(default_factory=time.time)


class UserStore:
    """用户内存存储 (Phase 1)."""

    def __init__(self) -> None:
        self._users: dict[str, User] = {}
        self._by_username: dict[str, str] = {}

    def _hash_password(self, password: str) -> str:
        return hashlib.sha256(
            (password + settings.SECRET_KEY).encode()
        ).hexdigest()

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        org_id: str = "",
        role: Role = Role.MEMBER,
    ) -> User:
        """创建用户."""
        if username in self._by_username:
            raise ValueError(f"用户名已存在: {username}")

        import uuid

        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            username=username,
            email=email,
            password_hash=self._hash_password(password),
            org_id=org_id,
            role=role,
        )
        self._users[user_id] = user
        self._by_username[username] = user_id
        return user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """认证用户."""
        uid = self._by_username.get(username)
        if not uid:
            return None
        user = self._users[uid]
        if user.password_hash != self._hash_password(password):
            return None
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        return self._users.get(user_id)


user_store = UserStore()

# 创建默认管理员
try:
    user_store.create_user(
        username="admin",
        email="admin@openagent.dev",
        password="admin123",
        role=Role.ADMIN,
    )
except ValueError:
    pass
