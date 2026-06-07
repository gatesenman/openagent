"""上下文预算管理 / Context Budget Manager.

把 LLM 的 token 窗口当"预算"管理：
- 自动压缩历史对话
- 增量注入代码（按需加载，不一次性塞满）
- Prompt 缓存策略
- 观察结果压缩
"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ContextBudget:
    """上下文预算配置."""
    max_tokens: int = 128000
    system_prompt_tokens: int = 2000
    tool_definitions_tokens: int = 3000
    history_tokens: int = 40000
    code_context_tokens: int = 60000
    working_memory_tokens: int = 20000
    reserved_tokens: int = 3000  # 留给 LLM 响应

    @property
    def available_tokens(self) -> int:
        return self.max_tokens - self.reserved_tokens


@dataclass
class ContextEntry:
    """上下文条目."""
    role: str  # system / user / assistant / tool
    content: str
    token_count: int = 0
    priority: int = 5  # 1-10, 10=最高优先级
    is_compressed: bool = False
    source: str = ""  # conversation / code / knowledge / tool_result


class ContextManager:
    """上下文预算管理器.

    核心思想：像管理内存一样管理 token 窗口。
    高优先级信息保留，低优先级信息压缩或丢弃。
    """

    def __init__(self, budget: ContextBudget | None = None):
        self.budget = budget or ContextBudget()
        self._entries: list[ContextEntry] = []
        self._total_tokens = 0
        self._compression_count = 0

    def add_entry(
        self, role: str, content: str,
        priority: int = 5, source: str = "conversation",
    ) -> ContextEntry:
        """添加上下文条目."""
        token_count = self._estimate_tokens(content)
        entry = ContextEntry(
            role=role, content=content,
            token_count=token_count, priority=priority,
            source=source,
        )
        self._entries.append(entry)
        self._total_tokens += token_count

        # 超出预算时自动压缩
        if self._total_tokens > self.budget.available_tokens:
            self._compress()

        return entry

    def get_messages(self) -> list[dict]:
        """获取当前上下文消息列表（适配 LLM API 格式）."""
        return [
            {"role": e.role, "content": e.content}
            for e in self._entries
        ]

    def _estimate_tokens(self, text: str) -> int:
        """粗略估算 token 数（1 token ≈ 4 字符 英文 / 2 字符中文）."""
        ascii_chars = sum(1 for c in text if ord(c) < 128)
        non_ascii = len(text) - ascii_chars
        return (ascii_chars // 4) + (non_ascii // 2) + 1

    def _compress(self):
        """压缩低优先级条目以释放 token 预算."""
        # 按优先级排序，压缩最低优先级的条目
        sortable = [
            (i, e) for i, e in enumerate(self._entries)
            if not e.is_compressed and e.role != "system"
        ]
        sortable.sort(key=lambda x: x[1].priority)

        for idx, entry in sortable:
            if self._total_tokens <= self.budget.available_tokens * 0.8:
                break

            original_tokens = entry.token_count
            compressed = self._summarize(entry.content)
            new_tokens = self._estimate_tokens(compressed)

            self._entries[idx] = ContextEntry(
                role=entry.role,
                content=compressed,
                token_count=new_tokens,
                priority=entry.priority,
                is_compressed=True,
                source=entry.source,
            )
            self._total_tokens -= (original_tokens - new_tokens)
            self._compression_count += 1

        logger.info(
            "上下文压缩完成: tokens=%d/%d, 压缩次数=%d",
            self._total_tokens, self.budget.available_tokens,
            self._compression_count,
        )

    def _summarize(self, text: str) -> str:
        """压缩文本（Phase 1: 简单截断 + 保留首尾）."""
        max_chars = 500
        if len(text) <= max_chars:
            return text
        head = text[:200]
        tail = text[-200:]
        return f"{head}\n...[已压缩 {len(text)} 字符]...\n{tail}"

    def get_stats(self) -> dict:
        """获取上下文统计."""
        return {
            "total_tokens": self._total_tokens,
            "max_tokens": self.budget.max_tokens,
            "available_tokens": self.budget.available_tokens,
            "utilization": round(self._total_tokens / self.budget.available_tokens * 100, 1),
            "entry_count": len(self._entries),
            "compression_count": self._compression_count,
            "entries_by_source": self._count_by_source(),
        }

    def _count_by_source(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for e in self._entries:
            counts[e.source] = counts.get(e.source, 0) + 1
        return counts

    def clear(self):
        """清空上下文."""
        self._entries.clear()
        self._total_tokens = 0
