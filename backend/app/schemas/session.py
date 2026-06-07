"""会话 Pydantic schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    title: str = Field(default="新会话", description="会话标题")
    mode: str = Field(default="cloud", description="运行模式: localhost/cascade/cloud")
    model: str = Field(default="gpt-4o", description="LLM 模型")
    platform: str = Field(default="linux", description="平台: linux/windows")
    language: str = Field(default="zh", description="语言: zh/en")
    prompt: str = Field(default="", description="初始任务描述")


class SessionUpdate(BaseModel):
    title: str | None = None
    status: str | None = None
    mode: str | None = None
    model: str | None = None


class SessionResponse(BaseModel):
    id: str
    title: str
    status: str
    mode: str
    model: str
    platform: str
    language: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SessionList(BaseModel):
    sessions: list[SessionResponse]
    total: int


class MessageCreate(BaseModel):
    content: str = Field(..., description="消息内容")


class MessageResponse(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    tool_calls: dict | list | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class EventResponse(BaseModel):
    id: int
    session_id: str
    event_type: str
    title: str
    content: str | None = None
    metadata_: dict | None = Field(None, alias="metadata")
    duration_ms: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
