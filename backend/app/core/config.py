"""应用配置 / Application configuration."""

from pydantic import model_validator
from pydantic_settings import BaseSettings

# Per-provider defaults used when LLM_BASE_URL is unset.
_PROVIDER_DEFAULT_BASE_URLS: dict[str, str] = {
    "openai": "https://api.openai.com/v1",
    "deepseek": "https://api.deepseek.com/v1",
    "qwen": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "anthropic": "https://api.anthropic.com/v1",
    "claude": "https://api.anthropic.com/v1",
    "ollama": "http://localhost:11434/v1",
    "local": "http://localhost:11434/v1",
}

# Maps LLM_PROVIDER to the vendor-specific env fields on Settings.
_PROVIDER_VENDOR_FIELDS: dict[str, tuple[str, str]] = {
    "openai": ("OPENAI_API_KEY", "OPENAI_BASE_URL"),
    "deepseek": ("DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL"),
    "qwen": ("QWEN_API_KEY", "QWEN_BASE_URL"),
    "anthropic": ("ANTHROPIC_API_KEY", "ANTHROPIC_BASE_URL"),
    "claude": ("ANTHROPIC_API_KEY", "ANTHROPIC_BASE_URL"),
    "ollama": ("", "OLLAMA_BASE_URL"),
    "local": ("", "OLLAMA_BASE_URL"),
}


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

    # LLM — the backend reads these fields. LLM_API_KEY / LLM_BASE_URL are
    # the primary settings. If they are empty, the selected LLM_PROVIDER's
    # vendor-specific variables (OPENAI_API_KEY, DEEPSEEK_API_KEY, ...) are
    # used as a fallback so a .env written against the older example still
    # works.
    LLM_PROVIDER: str = "openai"  # openai / deepseek / qwen / anthropic / ollama
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o"
    LLM_BASE_URL: str = ""

    # Optional vendor-specific keys (fallback only; not read by the LLM
    # client directly).
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = ""
    QWEN_API_KEY: str = ""
    QWEN_BASE_URL: str = ""
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_BASE_URL: str = ""
    OLLAMA_BASE_URL: str = ""

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

    @model_validator(mode="after")
    def resolve_vendor_llm_settings(self) -> "Settings":
        provider = (self.LLM_PROVIDER or "openai").strip().lower()
        key_field, url_field = _PROVIDER_VENDOR_FIELDS.get(
            provider, _PROVIDER_VENDOR_FIELDS["openai"]
        )
        if not self.LLM_API_KEY and key_field:
            self.LLM_API_KEY = getattr(self, key_field, "") or ""
        if not self.LLM_BASE_URL:
            vendor_url = getattr(self, url_field, "") if url_field else ""
            self.LLM_BASE_URL = vendor_url or _PROVIDER_DEFAULT_BASE_URLS.get(
                provider, ""
            )
        return self


settings = Settings()
