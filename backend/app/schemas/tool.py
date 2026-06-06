"""工具 Pydantic schemas."""

from pydantic import BaseModel, Field


class ToolSchema(BaseModel):
    """工具定义 schema（MCP 兼容）."""

    name: str
    description: str
    description_zh: str | None = None
    parameters: dict = Field(default_factory=dict, description="JSON Schema")
    category: str = "builtin"
    enabled: bool = True


class ToolExecuteRequest(BaseModel):
    """工具执行请求."""

    name: str
    arguments: dict = Field(default_factory=dict)


class ToolExecuteResponse(BaseModel):
    """工具执行响应."""

    success: bool
    output: str
    error: str | None = None
    duration_ms: int | None = None
