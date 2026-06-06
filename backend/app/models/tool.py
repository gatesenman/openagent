"""工具注册数据模型 / Tool registry data models."""

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, JSON

from app.core.database import Base


class Tool(Base):
    """注册的工具."""

    __tablename__ = "tools"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    description_zh = Column(Text, nullable=True)
    parameters_schema = Column(JSON, nullable=True)
    category = Column(String(50), default="builtin")  # builtin / mcp / custom
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
