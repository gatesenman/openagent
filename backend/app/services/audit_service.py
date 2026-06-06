"""审计日志服务 / Audit log service.

记录所有关键操作，支持合规查询和导出。
"""

import logging
import time
import uuid
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AuditEntry:
    """审计日志条目."""
    id: str
    timestamp: float
    user_id: str
    session_id: str | None = None
    action: str = ""
    resource_type: str = ""  # session / file / sandbox / tool / secret
    resource_id: str = ""
    detail: str = ""
    ip_address: str = ""
    severity: str = "info"  # info / warning / critical

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "detail": self.detail,
            "ip_address": self.ip_address,
            "severity": self.severity,
        }


class AuditService:
    """审计日志管理.

    Phase 1: 内存存储。
    Phase 2: 持久化到 PostgreSQL + HMAC 签名。
    """

    def __init__(self):
        self._entries: list[AuditEntry] = []
        self._max_entries = 10000

    def log(
        self,
        user_id: str,
        action: str,
        resource_type: str = "",
        resource_id: str = "",
        detail: str = "",
        session_id: str | None = None,
        ip_address: str = "",
        severity: str = "info",
    ) -> AuditEntry:
        """记录审计日志."""
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            timestamp=time.time(),
            user_id=user_id,
            session_id=session_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            detail=detail,
            ip_address=ip_address,
            severity=severity,
        )
        self._entries.append(entry)

        # 限制内存中的条目数
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]

        logger.debug("审计: [%s] %s %s/%s", severity, action, resource_type, resource_id)
        return entry

    def query(
        self,
        user_id: str | None = None,
        session_id: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        severity: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """查询审计日志."""
        results = self._entries[:]
        if user_id:
            results = [e for e in results if e.user_id == user_id]
        if session_id:
            results = [e for e in results if e.session_id == session_id]
        if action:
            results = [e for e in results if e.action == action]
        if resource_type:
            results = [e for e in results if e.resource_type == resource_type]
        if severity:
            results = [e for e in results if e.severity == severity]

        # 按时间倒序
        results.sort(key=lambda e: e.timestamp, reverse=True)
        return [e.to_dict() for e in results[offset:offset + limit]]

    def count(self) -> int:
        return len(self._entries)

    def export(self, format: str = "json") -> list[dict]:
        """导出全部审计日志."""
        return [e.to_dict() for e in self._entries]


audit_service = AuditService()
