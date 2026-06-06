"""应用配置 / Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """全局配置，从环境变量读取."""

    APP_NAME: str = "OpenAgent"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # 数据库
    DATABASE_URL: str = "sqlite:///./openagent.db"

    # JWT
    SECRET_KEY: str = "openagent-dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720

    # LLM
    LLM_PROVIDER: str = "openai"  # openai / deepseek / qwen
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o"
    LLM_BASE_URL: str = ""

    # Agent
    AGENT_MAX_ITERATIONS: int = 50
    AGENT_MAX_TOKENS_PER_TURN: int = 8192
    CONTEXT_WINDOW_SIZE: int = 128000
    CONTEXT_RESERVE_TOKENS: int = 16384

    # Sandbox
    SANDBOX_TYPE: str = "docker"  # docker / kvm
    SANDBOX_IMAGE: str = "ubuntu:22.04"
    SANDBOX_TIMEOUT: int = 3600

    # MCP
    MCP_ENABLED: bool = True

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
