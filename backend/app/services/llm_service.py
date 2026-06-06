"""LLM 调用服务 / LLM service.

支持多模型提供商：OpenAI / DeepSeek / Qwen / Claude。
根据会话模式和配置自动选择 provider。
"""

import logging
from dataclasses import dataclass
from typing import Any, AsyncIterator

from app.core.config import settings

logger = logging.getLogger(__name__)

# 模型到 provider 的映射
MODEL_PROVIDERS: dict[str, dict[str, str]] = {
    # OpenAI
    "gpt-4o": {"provider": "openai", "base_url": "https://api.openai.com/v1"},
    "gpt-4o-mini": {"provider": "openai", "base_url": "https://api.openai.com/v1"},
    "gpt-4.1": {"provider": "openai", "base_url": "https://api.openai.com/v1"},
    # DeepSeek（国内低延迟推荐）
    "deepseek-chat": {"provider": "deepseek", "base_url": "https://api.deepseek.com/v1"},
    "deepseek-coder": {"provider": "deepseek", "base_url": "https://api.deepseek.com/v1"},
    "deepseek-reasoner": {"provider": "deepseek", "base_url": "https://api.deepseek.com/v1"},
    # Qwen（阿里通义）
    "qwen-turbo": {"provider": "qwen", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
    "qwen-plus": {"provider": "qwen", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
    "qwen-max": {"provider": "qwen", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
    # Claude（通过 OpenAI 兼容 API）
    "claude-sonnet-4": {"provider": "claude", "base_url": "https://api.anthropic.com/v1"},
    "claude-3.5-sonnet": {"provider": "claude", "base_url": "https://api.anthropic.com/v1"},
    # 本地模型（localhost 模式，Ollama）
    "llama3": {"provider": "local", "base_url": "http://localhost:11434/v1"},
    "codellama": {"provider": "local", "base_url": "http://localhost:11434/v1"},
    "qwen2.5-coder": {"provider": "local", "base_url": "http://localhost:11434/v1"},
}


@dataclass
class LLMResponse:
    """LLM 响应."""
    content: str
    tool_calls: list[dict] | None = None
    usage: dict | None = None
    model: str = ""
    finish_reason: str = ""


class LLMService:
    """多模型 LLM 调用服务.

    根据模型名称自动路由到对应的 provider。
    支持同步调用和流式调用。
    """

    def __init__(self):
        self._clients: dict[str, Any] = {}

    def _get_client(self, model: str) -> Any:
        """获取或创建 OpenAI 兼容客户端."""
        info = MODEL_PROVIDERS.get(model)
        if not info:
            info = {"provider": "openai", "base_url": settings.LLM_BASE_URL or "https://api.openai.com/v1"}

        cache_key = info["base_url"]
        if cache_key not in self._clients:
            try:
                from openai import AsyncOpenAI
                api_key = settings.LLM_API_KEY or "sk-placeholder"
                self._clients[cache_key] = AsyncOpenAI(
                    api_key=api_key,
                    base_url=info["base_url"],
                )
            except ImportError:
                logger.warning("openai SDK 未安装")
                return None

        return self._clients[cache_key]

    async def chat(
        self,
        messages: list[dict],
        model: str = "",
        tools: list[dict] | None = None,
        temperature: float = 0.1,
        max_tokens: int = 8192,
    ) -> LLMResponse:
        """调用 LLM（同步模式）."""
        model = model or settings.LLM_MODEL
        client = self._get_client(model)

        if not client or not settings.LLM_API_KEY:
            return self._mock_response(messages, model)

        try:
            kwargs: dict[str, Any] = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            if tools:
                kwargs["tools"] = tools

            response = await client.chat.completions.create(**kwargs)
            choice = response.choices[0]

            tool_calls_data = None
            if choice.message.tool_calls:
                tool_calls_data = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in choice.message.tool_calls
                ]

            return LLMResponse(
                content=choice.message.content or "",
                tool_calls=tool_calls_data,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                model=model,
                finish_reason=choice.finish_reason or "",
            )
        except Exception as e:
            logger.error("LLM 调用失败 [%s]: %s", model, e)
            return self._mock_response(messages, model, error=str(e))

    async def stream_chat(
        self,
        messages: list[dict],
        model: str = "",
        tools: list[dict] | None = None,
        temperature: float = 0.1,
        max_tokens: int = 8192,
    ) -> AsyncIterator[dict]:
        """流式调用 LLM."""
        model = model or settings.LLM_MODEL
        client = self._get_client(model)

        if not client or not settings.LLM_API_KEY:
            yield {"type": "content", "delta": f"[Mock模式] 请配置 LLM_API_KEY 以启用 {model}"}
            return

        try:
            kwargs: dict[str, Any] = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": True,
            }
            if tools:
                kwargs["tools"] = tools

            response = await client.chat.completions.create(**kwargs)

            async for chunk in response:
                delta = chunk.choices[0].delta if chunk.choices else None
                if not delta:
                    continue

                if delta.content:
                    yield {"type": "content", "delta": delta.content}

                if delta.tool_calls:
                    for tc in delta.tool_calls:
                        yield {
                            "type": "tool_call",
                            "index": tc.index,
                            "id": tc.id,
                            "function_name": tc.function.name if tc.function else None,
                            "function_args": tc.function.arguments if tc.function else None,
                        }

                if chunk.choices[0].finish_reason:
                    yield {"type": "finish", "reason": chunk.choices[0].finish_reason}

        except Exception as e:
            logger.error("LLM 流式调用失败 [%s]: %s", model, e)
            yield {"type": "error", "error": str(e)}

    def _mock_response(
        self, messages: list[dict], model: str, error: str = ""
    ) -> LLMResponse:
        """Mock 响应（无 API key 时）."""
        last_user = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user = m.get("content", "")[:200]
                break

        content = (
            f"[Mock模式 - {model}] 收到消息: {last_user}\n\n"
            "请在设置中配置 LLM API Key 以启用真实推理。\n"
            "支持: OpenAI / DeepSeek / Qwen / Claude / 本地模型(Ollama)"
        )
        if error:
            content = f"[错误] {error}\n\n{content}"

        return LLMResponse(content=content, model=model, finish_reason="mock")


# 全局单例
llm_service = LLMService()
