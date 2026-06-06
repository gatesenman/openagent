"""会话数据模型 / Session data models."""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class SessionStatus(str, Enum):
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentMode(str, Enum):
    LOCALHOST = "localhost"
    CASCADE = "cascade"
    CLOUD = "cloud"


class Session(Base):
    """Agent 会话."""

    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, default="新会话")
    status = Column(String(20), default=SessionStatus.CREATED)
    mode = Column(String(20), default=AgentMode.CLOUD)
    model = Column(String(50), default="gpt-4o")
    platform = Column(String(20), default="linux")  # linux / windows
    language = Column(String(10), default="zh")  # zh / en

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("Message", back_populates="session", cascade="all, delete")
    events = relationship("Event", back_populates="session", cascade="all, delete")


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class Message(Base):
    """会话消息."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    tool_calls = Column(JSON, nullable=True)
    tool_call_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="messages")


class EventType(str, Enum):
    THINK = "think"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    CODE_EDIT = "code_edit"
    SHELL_EXEC = "shell_exec"
    FILE_READ = "file_read"
    SEARCH = "search"
    ERROR = "error"
    PLAN_UPDATE = "plan_update"


class Event(Base):
    """Agent 事件（Worklog 条目）."""

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("sessions.id"), nullable=False)
    event_type = Column(String(30), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSON, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("Session", back_populates="events")
