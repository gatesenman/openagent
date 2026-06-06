"""API Keys / Service Users 管理服务.

管理编程式 API 访问的 Service Users 和 API Keys。
"""

import hashlib
import logging
import secrets
import time
import uuid
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ServiceUser:
    """Service User（API 访问用户）."""
    id: str
    name: str
    description: str = ""
    api_key_prefix: str = ""  # 显示用前缀 "oa_...abc"
    api_key_hash: str = ""    # 完整 key 的 hash
    permissions: list[str] = field(default_factory=lambda: ["read"])
    created_at: float = field(default_factory=time.time)
    last_used_at: float | None = None
    is_active: bool = True

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "api_key_prefix": self.api_key_prefix,
            "permissions": self.permissions,
            "created_at": self.created_at,
            "last_used_at": self.last_used_at,
            "is_active": self.is_active,
        }


class APIKeysService:
    """API Keys 管理."""

    def __init__(self):
        self._service_users: dict[str, ServiceUser] = {}
        self._key_to_user: dict[str, str] = {}  # key_hash -> user_id

    def create_service_user(
        self, name: str, description: str = "",
        permissions: list[str] | None = None,
    ) -> tuple[ServiceUser, str]:
        """创建 Service User 并生成 API Key.

        返回 (ServiceUser, raw_api_key)。
        raw_api_key 仅在创建时返回一次，之后无法再获取。
        """
        user_id = str(uuid.uuid4())
        raw_key = f"oa_{secrets.token_urlsafe(32)}"
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        user = ServiceUser(
            id=user_id,
            name=name,
            description=description,
            api_key_prefix=raw_key[:8] + "..." + raw_key[-4:],
            api_key_hash=key_hash,
            permissions=permissions or ["read"],
        )
        self._service_users[user_id] = user
        self._key_to_user[key_hash] = user_id
        logger.info("Service User 已创建: %s", name)
        return user, raw_key

    def list_service_users(self) -> list[dict]:
        return [u.to_dict() for u in self._service_users.values()]

    def get_service_user(self, user_id: str) -> ServiceUser | None:
        return self._service_users.get(user_id)

    def validate_api_key(self, api_key: str) -> ServiceUser | None:
        """验证 API Key 并返回对应的 Service User."""
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        user_id = self._key_to_user.get(key_hash)
        if not user_id:
            return None
        user = self._service_users.get(user_id)
        if user and user.is_active:
            user.last_used_at = time.time()
            return user
        return None

    def delete_service_user(self, user_id: str) -> bool:
        user = self._service_users.get(user_id)
        if not user:
            return False
        # 移除 key 映射
        self._key_to_user = {
            k: v for k, v in self._key_to_user.items() if v != user_id
        }
        del self._service_users[user_id]
        logger.info("Service User 已删除: %s", user.name)
        return True

    def toggle_service_user(self, user_id: str) -> ServiceUser | None:
        user = self._service_users.get(user_id)
        if not user:
            return None
        user.is_active = not user.is_active
        return user


apikeys_service = APIKeysService()
