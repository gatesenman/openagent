"""Agent Pydantic schemas."""

from pydantic import BaseModel, Field


class AgentConfig(BaseModel):
    """Agent 配置."""

    model: str = Field(default="gpt-4o", description="LLM 模型")
    max_iterations: int = Field(default=50, description="最大迭代次数")
    max_tokens_per_turn: int = Field(default=8192, description="每轮最大 token")
    temperature: float = Field(default=0.1, description="采样温度")
    tools_enabled: list[str] = Field(
        default=["shell_exec", "file_read", "file_write", "search_code", "git_ops"],
        description="启用的工具列表",
    )
    safe_mode: bool = Field(default=True, description="安全模式（危险操作需确认）")


class AgentEvent(BaseModel):
    """AG-UI 标准事件."""

    type: str  # TEXT_MESSAGE_START, TOOL_CALL_START, etc.
    message_id: str | None = None
    tool_call_id: str | None = None
    tool_name: str | None = None
    delta: str | None = None
    args: dict | None = None
    step: str | None = None
    content: str | None = None
    error: str | None = None


class ToolCallRequest(BaseModel):
    """工具调用请求."""

    tool_name: str
    arguments: dict = Field(default_factory=dict)


class ToolCallResult(BaseModel):
    """工具调用结果."""

    tool_call_id: str
    tool_name: str
    success: bool
    output: str
    error: str | None = None
    duration_ms: int | None = None
