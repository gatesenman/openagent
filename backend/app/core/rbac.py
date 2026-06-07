"""RBAC 中间件 / Role-Based Access Control middleware.

提供路由级别的权限控制。
"""

import logging
from enum import Enum
from functools import wraps
from typing import Any, Callable

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.auth import Role, verify_token

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


class Permission(str, Enum):
    """细粒度权限."""
    SESSION_CREATE = "session:create"
    SESSION_READ = "session:read"
    SESSION_DELETE = "session:delete"
    KNOWLEDGE_CREATE = "knowledge:create"
    KNOWLEDGE_READ = "knowledge:read"
    KNOWLEDGE_DELETE = "knowledge:delete"
    PLAYBOOK_CREATE = "playbook:create"
    PLAYBOOK_READ = "playbook:read"
    PLAYBOOK_EXECUTE = "playbook:execute"
    SETTINGS_READ = "settings:read"
    SETTINGS_WRITE = "settings:write"
    AUTOMATION_MANAGE = "automation:manage"
    ANALYTICS_READ = "analytics:read"
    ADMIN_ALL = "admin:all"


# 角色 -> 权限映射
ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.ADMIN: {p for p in Permission},  # 全部权限
    Role.MEMBER: {
        Permission.SESSION_CREATE,
        Permission.SESSION_READ,
        Permission.KNOWLEDGE_CREATE,
        Permission.KNOWLEDGE_READ,
        Permission.PLAYBOOK_READ,
        Permission.PLAYBOOK_EXECUTE,
        Permission.SETTINGS_READ,
        Permission.ANALYTICS_READ,
    },
    Role.VIEWER: {
        Permission.SESSION_READ,
        Permission.KNOWLEDGE_READ,
        Permission.PLAYBOOK_READ,
        Permission.ANALYTICS_READ,
    },
}


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict | None:
    """可选的用户认证（不强制）."""
    if not credentials:
        return None
    try:
        payload = verify_token(credentials.credentials)
        if payload:
            return {"user_id": payload.sub, "role": payload.role.value, "org_id": payload.org_id}
        return None
    except Exception:
        return None


async def get_current_user_required(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """强制用户认证."""
    if not credentials:
        raise HTTPException(status_code=401, detail="未提供认证凭证")
    try:
        payload = verify_token(credentials.credentials)
        if not payload:
            raise HTTPException(status_code=401, detail="无效凭证")
        return {"user_id": payload.sub, "role": payload.role.value, "org_id": payload.org_id}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))


def require_permission(*permissions: Permission):
    """权限检查依赖注入."""
    async def _check(
        user: dict = Depends(get_current_user_required),
    ) -> dict:
        role = Role(user.get("role", "viewer"))
        user_perms = ROLE_PERMISSIONS.get(role, set())
        for perm in permissions:
            if perm not in user_perms:
                raise HTTPException(
                    status_code=403,
                    detail=f"权限不足: 需要 {perm.value}",
                )
        return user
    return _check


def require_role(min_role: Role):
    """角色级别检查."""
    role_levels = {Role.VIEWER: 0, Role.MEMBER: 1, Role.ADMIN: 2}

    async def _check(
        user: dict = Depends(get_current_user_required),
    ) -> dict:
        user_role = Role(user.get("role", "viewer"))
        if role_levels.get(user_role, 0) < role_levels.get(min_role, 0):
            raise HTTPException(
                status_code=403,
                detail=f"需要 {min_role.value} 角色或更高",
            )
        return user
    return _check
