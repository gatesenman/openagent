"""密钥管理服务 / Secrets management service.

加密存储敏感信息（API Keys / 密码 / 证书）。
仅返回名称列表，不暴露实际值。
"""

import hashlib
import hmac
import logging
import time
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Secret:
    """密钥条目."""
    id: str
    name: str
    scope: str  # org / user / repo
    created_by: str = ""
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    repo_name: str | None = None
    # 加密存储 — 内存中仅保留加密后的值
    _encrypted_value: str = field(default="", repr=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "scope": self.scope,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "repo_name": self.repo_name,
        }


class SecretsService:
    """密钥管理.

    Phase 1: 内存存储 + 简单加密。
    Phase 2: 迁移到 HashiCorp Vault / AWS KMS。
    """

    def __init__(self):
        self._secrets: dict[str, Secret] = {}
        self._encryption_key = "openagent-secrets-key-phase1"

    def _encrypt(self, value: str) -> str:
        """简单加密 (Phase 1, 后续替换为 AES-256-GCM)."""
        key = hashlib.sha256(self._encryption_key.encode()).digest()
        sig = hmac.new(key, value.encode(), hashlib.sha256).hexdigest()
        return sig + ":" + value[::-1]  # 简单混淆，Phase 2 用真加密

    def _decrypt(self, encrypted: str) -> str:
        """解密."""
        parts = encrypted.split(":", 1)
        if len(parts) != 2:
            return ""
        return parts[1][::-1]

    def create_secret(
        self,
        name: str,
        value: str,
        scope: str = "org",
        created_by: str = "",
        repo_name: str | None = None,
    ) -> Secret:
        """创建密钥."""
        import uuid
        secret_id = str(uuid.uuid4())
        secret = Secret(
            id=secret_id,
            name=name,
            scope=scope,
            created_by=created_by,
            repo_name=repo_name,
            _encrypted_value=self._encrypt(value),
        )
        self._secrets[secret_id] = secret
        logger.info("密钥已创建: %s [scope=%s]", name, scope)
        return secret

    def list_secrets(
        self, scope: str | None = None, repo_name: str | None = None,
    ) -> list[dict]:
        """列出密钥（仅名称，不含值）."""
        results = []
        for s in self._secrets.values():
            if scope and s.scope != scope:
                continue
            if repo_name and s.repo_name != repo_name:
                continue
            results.append(s.to_dict())
        return results

    def get_secret_value(self, secret_id: str) -> str | None:
        """获取密钥值（仅 Agent 内部使用，不暴露给 API）."""
        secret = self._secrets.get(secret_id)
        if not secret:
            return None
        return self._decrypt(secret._encrypted_value)

    def delete_secret(self, secret_id: str) -> bool:
        """删除密钥."""
        if secret_id in self._secrets:
            name = self._secrets[secret_id].name
            del self._secrets[secret_id]
            logger.info("密钥已删除: %s", name)
            return True
        return False

    def update_secret(self, secret_id: str, value: str) -> bool:
        """更新密钥值."""
        secret = self._secrets.get(secret_id)
        if not secret:
            return False
        secret._encrypted_value = self._encrypt(value)
        secret.updated_at = time.time()
        return True


secrets_service = SecretsService()
