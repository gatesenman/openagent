"""审计日志模型 / Audit Log model.

记录所有 Agent 操作, 支持 SOC2/等保合规。
"""

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.sql import func

from app.core.database import Base


class AuditLog(Base):
    """审计日志表."""

    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=func.now(), index=True)
    user_id = Column(String(36), index=True)
    session_id = Column(String(36), index=True)
    action = Column(String(64), nullable=False, index=True)
    resource_type = Column(String(32))  # session / file / sandbox / tool
    resource_id = Column(String(255))
    detail = Column(Text)
    ip_address = Column(String(45))
    # HMAC 签名防篡改 (Phase 2)
    signature = Column(String(128))
