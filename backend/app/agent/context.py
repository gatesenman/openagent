"""上下文管理器 / Context manager.

管理 LLM 上下文窗口，确保不超过 token 预算。
实现上下文压缩、摘要和增量注入策略。
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# tiktoken 可选依赖
try:
    import tiktoken
    _encoder = tiktoken.get_encoding("cl100k_base")
except ImportError:
    _encoder = None
    logger.warning("tiktoken 未安装，使用近似 token 计数")


def count_tokens(text: str) -> int:
    """计算文本的 token 数."""
    if _encoder:
        return len(_encoder.encode(text))
    # 近似估算：英文约4字符/token，中文约2字符/token
    return len(text) // 3


SYSTEM_PROMPT_ZH = """你是 OpenAgent，一个 AI 驱动的全栈软件开发助手。
你在一个隔离的虚拟环境（沙箱）中工作，可以执行 shell 命令、读写文件、搜索代码、执行 Git 操作。

## 工作模式
你使用 ReAct（Reasoning + Acting）循环工作：
1. **Think（思考）**: 分析当前状态和目标，制定下一步计划
2. **Act（行动）**: 调用工具执行操作
3. **Observe（观察）**: 检查工具返回的结果
4. **Reflect（反思）**: 评估进展，决定是否继续或调整策略

## 核心原则
- 零幻觉：所有代码必须在真实环境中验证，不要假设文件内容或命令结果
- 先读后写：修改文件前先读取当前内容
- 增量执行：每步只做一件事，验证后再继续
- 错误恢复：遇到错误时分析原因并重试，连续3次相同错误则切换策略

## 安全限制
- 不执行危险命令（rm -rf /, DROP TABLE 等）
- 不修改系统关键文件
- 不暴露敏感信息（密钥、密码等）
"""

SYSTEM_PROMPT_EN = """You are OpenAgent, an AI-powered full-stack software development assistant.
You work in an isolated virtual environment (sandbox) where you can execute shell commands, read/write files, search code, and perform Git operations.

## Working Mode
You use the ReAct (Reasoning + Acting) loop:
1. **Think**: Analyze current state and goals, plan next step
2. **Act**: Call tools to execute operations
3. **Observe**: Check tool results
4. **Reflect**: Evaluate progress, decide whether to continue or adjust strategy

## Core Principles
- Zero hallucination: All code must be verified in real environment
- Read before write: Always read file contents before modifying
- Incremental execution: Do one thing at a time, verify before continuing
- Error recovery: Analyze errors and retry, switch strategy after 3 same errors

## Safety Constraints
- No dangerous commands (rm -rf /, DROP TABLE, etc.)
- No modification of critical system files
- No exposure of sensitive information
"""


class ContextManager:
    """上下文窗口管理器.

    确保发送给 LLM 的消息在 token 预算内。
    策略：系统提示词(固定) + 会话摘要(压缩) + 最近消息 + 工具定义
    """

    def __init__(self, max_tokens: int = 128000, reserve_tokens: int = 16384):
        self.max_tokens = max_tokens
        self.reserve_tokens = reserve_tokens
        self.available_tokens = max_tokens - reserve_tokens

    def build_messages(
        self,
        history: list[dict[str, Any]],
        tools: list[dict] | None = None,
        language: str = "zh",
    ) -> list[dict[str, Any]]:
        """构建消息列表，确保在 token 预算内.

        Args:
            history: 完整的消息历史
            tools: 工具定义列表
            language: 语言 (zh/en)
        """
        system_prompt = SYSTEM_PROMPT_ZH if language == "zh" else SYSTEM_PROMPT_EN
        system_msg = {"role": "system", "content": system_prompt}

        # 计算固定开销
        system_tokens = count_tokens(system_prompt)
        tool_tokens = 0
        if tools:
            import json
            tool_tokens = count_tokens(json.dumps(tools))

        budget = self.available_tokens - system_tokens - tool_tokens

        # 从最新消息开始，向前填充
        selected: list[dict[str, Any]] = []
        used_tokens = 0

        for msg in reversed(history):
            msg_tokens = count_tokens(msg.get("content", ""))
            if used_tokens + msg_tokens > budget:
                break
            selected.insert(0, msg)
            used_tokens += msg_tokens

        return [system_msg] + selected

    def summarize_if_needed(
        self, history: list[dict[str, Any]], threshold: int = 50
    ) -> list[dict[str, Any]]:
        """如果消息数超过阈值，压缩早期消息为摘要.

        简单实现：保留最近 threshold 条消息，更早的消息合并为摘要。
        """
        if len(history) <= threshold:
            return history

        early = history[:-threshold]
        recent = history[-threshold:]

        # 简单摘要：提取关键操作
        summary_parts = []
        for msg in early:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "assistant" and len(content) > 100:
                summary_parts.append(content[:100] + "...")
            elif role == "tool":
                summary_parts.append(f"[工具结果] {content[:50]}...")

        summary = "以下是之前操作的摘要:\n" + "\n".join(summary_parts[-10:])
        summary_msg = {"role": "system", "content": summary}

        return [summary_msg] + recent
