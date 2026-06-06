"""Agent 自动记忆服务 / Auto Memory Service.

实现三级记忆体系:
- 短期记忆: 当前会话上下文
- 工作记忆: 近期会话的重要发现
- 长期记忆: 持久化知识 (→ Knowledge)
"""

import logging
import time
import uuid
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """记忆条目."""
    id: str = ""
    session_id: str = ""
    content: str = ""
    category: str = ""  # preference / pattern / error / convention / fact
    importance: float = 0.5  # 0-1
    tier: str = "short"  # short / working / long
    created_at: float = 0.0
    last_accessed: float = 0.0
    access_count: int = 0
    decay_rate: float = 0.1
    tags: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = time.time()
        if not self.last_accessed:
            self.last_accessed = self.created_at

    @property
    def effective_importance(self) -> float:
        """计算衰减后的有效重要性."""
        age_hours = (time.time() - self.last_accessed) / 3600
        decay = self.decay_rate * age_hours
        return max(0.0, self.importance - decay)


class MemoryService:
    """Agent 自动记忆管理.

    - 会话中自动发现重要信息
    - 跨会话记忆传递
    - 记忆分级与自动衰减
    """

    def __init__(self):
        self._memories: dict[str, MemoryEntry] = {}
        self._session_memories: dict[str, list[str]] = {}  # session_id → [memory_ids]

    def remember(
        self,
        content: str,
        session_id: str = "",
        category: str = "fact",
        importance: float = 0.5,
        tier: str = "short",
        tags: list[str] | None = None,
    ) -> MemoryEntry:
        """记录新记忆."""
        entry = MemoryEntry(
            session_id=session_id,
            content=content,
            category=category,
            importance=importance,
            tier=tier,
            tags=tags or [],
        )
        self._memories[entry.id] = entry
        if session_id:
            self._session_memories.setdefault(session_id, []).append(entry.id)
        return entry

    def recall(
        self,
        query: str = "",
        session_id: str = "",
        tier: str = "",
        category: str = "",
        limit: int = 20,
    ) -> list[MemoryEntry]:
        """检索记忆."""
        results: list[MemoryEntry] = []
        for mem in self._memories.values():
            if session_id and mem.session_id != session_id:
                continue
            if tier and mem.tier != tier:
                continue
            if category and mem.category != category:
                continue
            if query and query.lower() not in mem.content.lower():
                continue
            mem.last_accessed = time.time()
            mem.access_count += 1
            results.append(mem)

        results.sort(key=lambda m: m.effective_importance, reverse=True)
        return results[:limit]

    def promote(self, memory_id: str) -> MemoryEntry | None:
        """提升记忆层级: short → working → long."""
        mem = self._memories.get(memory_id)
        if not mem:
            return None
        tier_order = ["short", "working", "long"]
        idx = tier_order.index(mem.tier)
        if idx < len(tier_order) - 1:
            mem.tier = tier_order[idx + 1]
            mem.importance = min(1.0, mem.importance + 0.2)
        return mem

    def forget(self, memory_id: str) -> bool:
        """删除记忆."""
        mem = self._memories.pop(memory_id, None)
        if mem and mem.session_id in self._session_memories:
            ids = self._session_memories[mem.session_id]
            if memory_id in ids:
                ids.remove(memory_id)
        return mem is not None

    def auto_discover(self, text: str, session_id: str = "") -> list[MemoryEntry]:
        """从对话/工具输出中自动发现值得记忆的信息.

        Phase 1: 基于关键词匹配
        Phase 2: 使用 LLM 判断
        """
        discovered: list[MemoryEntry] = []
        patterns = {
            "preference": ["always use", "prefer", "don't use", "never", "我习惯", "总是用", "不要用"],
            "convention": ["naming convention", "code style", "file structure", "命名规范", "代码风格"],
            "error": ["error:", "failed:", "exception:", "traceback:", "错误:", "失败:"],
            "pattern": ["pattern:", "rule:", "important:", "note:", "规则:", "注意:"],
        }
        text_lower = text.lower()
        for category, keywords in patterns.items():
            for kw in keywords:
                if kw.lower() in text_lower:
                    entry = self.remember(
                        content=text[:500],
                        session_id=session_id,
                        category=category,
                        importance=0.7 if category != "error" else 0.5,
                        tier="working",
                    )
                    discovered.append(entry)
                    break
        return discovered

    def cleanup(self, threshold: float = 0.05) -> int:
        """清理衰减到阈值以下的短期记忆."""
        to_remove = [
            mid for mid, m in self._memories.items()
            if m.tier == "short" and m.effective_importance < threshold
        ]
        for mid in to_remove:
            self.forget(mid)
        return len(to_remove)

    def get_session_context(self, session_id: str) -> list[dict]:
        """获取会话相关的所有记忆, 用于注入上下文."""
        memories = self.recall(session_id=session_id, limit=50)
        working = self.recall(tier="working", limit=20)
        long_term = self.recall(tier="long", limit=10)

        seen = set()
        context = []
        for mem in memories + working + long_term:
            if mem.id not in seen:
                seen.add(mem.id)
                context.append({
                    "id": mem.id,
                    "content": mem.content,
                    "category": mem.category,
                    "tier": mem.tier,
                    "importance": round(mem.effective_importance, 3),
                })
        return context

    def get_stats(self) -> dict:
        """统计信息."""
        tiers = {"short": 0, "working": 0, "long": 0}
        for m in self._memories.values():
            tiers[m.tier] = tiers.get(m.tier, 0) + 1
        return {
            "total": len(self._memories),
            "by_tier": tiers,
            "sessions_tracked": len(self._session_memories),
        }


memory_service = MemoryService()
