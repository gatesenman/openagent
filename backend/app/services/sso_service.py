"""SSO / SAML / OIDC 认证骨架.

Phase 1: 提供接口框架和配置模型。
Phase 2: 接入实际 IdP (Okta / Azure AD / Google Workspace)。
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class SSOProvider(Enum):
    saml = "saml"
    oidc = "oidc"
    oauth2 = "oauth2"
    ldap = "ldap"


class SSOStatus(Enum):
    active = "active"
    inactive = "inactive"
    testing = "testing"


@dataclass
class SSOConfig:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    org_id: str = ""
    provider: SSOProvider = SSOProvider.saml
    name: str = ""
    status: SSOStatus = SSOStatus.inactive
    # SAML
    entity_id: str = ""
    sso_url: str = ""
    certificate: str = ""
    # OIDC
    client_id: str = ""
    client_secret_hash: str = ""
    issuer_url: str = ""
    # Common
    domain_whitelist: list = field(default_factory=list)
    auto_provision: bool = True
    default_role: str = "member"
    attribute_mapping: dict = field(default_factory=lambda: {
        "email": "email",
        "name": "displayName",
        "groups": "memberOf",
    })
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class SSOSession:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    config_id: str = ""
    user_email: str = ""
    user_name: str = ""
    groups: list = field(default_factory=list)
    provider: str = ""
    token: str = ""
    expires_at: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class SSOService:
    def __init__(self):
        self._configs: dict[str, SSOConfig] = {}

    def create_config(
        self,
        org_id: str,
        provider: str,
        name: str,
        **kwargs,
    ) -> SSOConfig:
        cfg = SSOConfig(
            org_id=org_id,
            provider=SSOProvider(provider),
            name=name,
            entity_id=kwargs.get("entity_id", ""),
            sso_url=kwargs.get("sso_url", ""),
            certificate=kwargs.get("certificate", ""),
            client_id=kwargs.get("client_id", ""),
            issuer_url=kwargs.get("issuer_url", ""),
            domain_whitelist=kwargs.get("domain_whitelist", []),
            auto_provision=kwargs.get("auto_provision", True),
            default_role=kwargs.get("default_role", "member"),
        )
        self._configs[cfg.id] = cfg
        return cfg

    def get_config(self, config_id: str) -> Optional[dict]:
        c = self._configs.get(config_id)
        if not c:
            return None
        return {
            "id": c.id,
            "org_id": c.org_id,
            "provider": c.provider.value,
            "name": c.name,
            "status": c.status.value,
            "entity_id": c.entity_id,
            "sso_url": c.sso_url,
            "client_id": c.client_id,
            "issuer_url": c.issuer_url,
            "domain_whitelist": c.domain_whitelist,
            "auto_provision": c.auto_provision,
            "default_role": c.default_role,
            "created_at": c.created_at,
        }

    def list_configs(self, org_id: str = "") -> list[dict]:
        results = []
        for c in self._configs.values():
            if org_id and c.org_id != org_id:
                continue
            results.append({
                "id": c.id,
                "provider": c.provider.value,
                "name": c.name,
                "status": c.status.value,
                "created_at": c.created_at,
            })
        return results

    def activate(self, config_id: str) -> bool:
        c = self._configs.get(config_id)
        if not c:
            return False
        c.status = SSOStatus.active
        return True

    def deactivate(self, config_id: str) -> bool:
        c = self._configs.get(config_id)
        if not c:
            return False
        c.status = SSOStatus.inactive
        return True

    def test_connection(self, config_id: str) -> dict:
        c = self._configs.get(config_id)
        if not c:
            return {"success": False, "error": "Config not found"}
        # Phase 1: 模拟测试
        c.status = SSOStatus.testing
        return {
            "success": True,
            "provider": c.provider.value,
            "sso_url": c.sso_url or c.issuer_url,
            "message": "Connection test successful (simulated)",
        }

    def initiate_login(self, config_id: str) -> Optional[dict]:
        c = self._configs.get(config_id)
        if not c or c.status != SSOStatus.active:
            return None
        if c.provider == SSOProvider.saml:
            return {
                "type": "redirect",
                "url": c.sso_url,
                "relay_state": str(uuid.uuid4()),
            }
        elif c.provider in (SSOProvider.oidc, SSOProvider.oauth2):
            return {
                "type": "redirect",
                "url": f"{c.issuer_url}/authorize?client_id={c.client_id}&response_type=code",
                "state": str(uuid.uuid4()),
            }
        return None

    def handle_callback(self, config_id: str, code: str = "", saml_response: str = "") -> Optional[SSOSession]:
        c = self._configs.get(config_id)
        if not c:
            return None
        # Phase 1: 模拟回调处理
        session = SSOSession(
            config_id=config_id,
            user_email="sso-user@example.com",
            user_name="SSO User",
            groups=["developers"],
            provider=c.provider.value,
            token=str(uuid.uuid4()),
        )
        return session

    def delete_config(self, config_id: str) -> bool:
        if config_id in self._configs:
            del self._configs[config_id]
            return True
        return False


sso_service = SSOService()
