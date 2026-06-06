"""用户模型 / User model.

SQLAlchemy ORM 定义 (Phase 2 PostgreSQL 使用)。
"""

from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, String
from sqlalchemy.sql import func

from app.core.database import Base


class UserModel(Base):
    """用户表."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    org_id = Column(String(36), default="", index=True)
    role = Column(String(16), default="member")
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
