"""多模型智能路由 / Model Router.

根据任务类型和复杂度自动选择最优模型：
- 简单任务（改变量名）→ Fast 模型（便宜快）
- 中等任务（写函数）  → Agent 模型（平衡）
- 复杂任务（重构模块）→ 强模型（贵但强）
- API 故障时自动降级到备选模型
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class TaskComplexity(str, Enum):
    SIMPLE = "simple"    # 改变量名、加注释
    MEDIUM = "medium"    # 写函数、修 bug
    COMPLEX = "complex"  # 重构模块、设计架构
    CRITICAL = "critical" # 安全修复、性能优化


@dataclass
class ModelInfo:
    """模型信息."""
    id: str
    provider: str
    name: str
    tier: str  # fast / agent / strong
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    max_tokens: int = 128000
    supports_tools: bool = True
    avg_latency_ms: float = 1000.0
    is_available: bool = True
    failure_count: int = 0
    last_failure_at: float | None = None


# 默认模型配置
DEFAULT_MODELS: list[ModelInfo] = [
    ModelInfo("gpt-4o-mini", "openai", "GPT-4o Mini", "fast",
             cost_per_1k_input=0.00015, cost_per_1k_output=0.0006, avg_latency_ms=500),
    ModelInfo("deepseek-chat", "deepseek", "DeepSeek Chat", "fast",
             cost_per_1k_input=0.00014, cost_per_1k_output=0.00028, avg_latency_ms=800),
    ModelInfo("gpt-4o", "openai", "GPT-4o", "agent",
             cost_per_1k_input=0.0025, cost_per_1k_output=0.01, avg_latency_ms=1500),
    ModelInfo("deepseek-coder", "deepseek", "DeepSeek Coder", "agent",
             cost_per_1k_input=0.00014, cost_per_1k_output=0.00028, avg_latency_ms=1000),
    ModelInfo("qwen-plus", "qwen", "Qwen Plus", "agent",
             cost_per_1k_input=0.0004, cost_per_1k_output=0.0012, avg_latency_ms=1200),
    ModelInfo("claude-sonnet-4", "claude", "Claude Sonnet 4", "strong",
             cost_per_1k_input=0.003, cost_per_1k_output=0.015, avg_latency_ms=2000),
    ModelInfo("gpt-4.1", "openai", "GPT-4.1", "strong",
             cost_per_1k_input=0.002, cost_per_1k_output=0.008, avg_latency_ms=2500),
    ModelInfo("deepseek-reasoner", "deepseek", "DeepSeek R1", "strong",
             cost_per_1k_input=0.00055, cost_per_1k_output=0.0022, avg_latency_ms=3000),
]


class ModelRouter:
    """多模型智能路由器."""

    def __init__(self, models: list[ModelInfo] | None = None):
        self._models = {m.id: m for m in (models or DEFAULT_MODELS)}
        self._usage_log: list[dict] = []
        self._total_cost = 0.0

    def classify_task(self, task_description: str) -> TaskComplexity:
        """根据任务描述自动分类复杂度."""
        desc_lower = task_description.lower()

        # 简单任务关键词
        simple_keywords = [
            "rename", "改名", "重命名", "add comment", "加注释",
            "fix typo", "修改文案", "update text", "change string",
        ]
        # 复杂任务关键词
        complex_keywords = [
            "refactor", "重构", "redesign", "架构", "migrate",
            "迁移", "implement", "实现", "全面", "系统",
        ]
        # 关键任务关键词
        critical_keywords = [
            "security", "安全", "vulnerability", "漏洞",
            "performance", "性能", "critical", "紧急",
        ]

        if any(kw in desc_lower for kw in critical_keywords):
            return TaskComplexity.CRITICAL
        if any(kw in desc_lower for kw in complex_keywords):
            return TaskComplexity.COMPLEX
        if any(kw in desc_lower for kw in simple_keywords):
            return TaskComplexity.SIMPLE
        return TaskComplexity.MEDIUM

    def select_model(
        self,
        task_description: str = "",
        complexity: TaskComplexity | None = None,
        preferred_provider: str | None = None,
    ) -> ModelInfo:
        """选择最优模型."""
        if not complexity:
            complexity = self.classify_task(task_description)

        # 复杂度到模型 tier 映射
        tier_map = {
            TaskComplexity.SIMPLE: "fast",
            TaskComplexity.MEDIUM: "agent",
            TaskComplexity.COMPLEX: "strong",
            TaskComplexity.CRITICAL: "strong",
        }
        target_tier = tier_map[complexity]

        # 筛选可用模型
        candidates = [
            m for m in self._models.values()
            if m.tier == target_tier and m.is_available
        ]

        # 如果目标 tier 没有可用模型，尝试降级
        if not candidates:
            all_available = [m for m in self._models.values() if m.is_available]
            if not all_available:
                # 重置所有模型为可用
                for m in self._models.values():
                    m.is_available = True
                    m.failure_count = 0
                all_available = list(self._models.values())
            candidates = all_available

        # 优先匹配 provider
        if preferred_provider:
            provider_match = [
                m for m in candidates if m.provider == preferred_provider
            ]
            if provider_match:
                candidates = provider_match

        # 按成本排序（同 tier 中选最便宜的）
        candidates.sort(key=lambda m: m.cost_per_1k_input)
        selected = candidates[0]

        logger.info(
            "模型路由: complexity=%s → model=%s (tier=%s, cost=$%.4f/1K)",
            complexity.value, selected.id, selected.tier, selected.cost_per_1k_input,
        )
        return selected

    def report_failure(self, model_id: str, error: str):
        """报告模型调用失败，触发自动降级."""
        model = self._models.get(model_id)
        if not model:
            return

        model.failure_count += 1
        model.last_failure_at = time.time()

        # 连续 3 次失败，标记为不可用
        if model.failure_count >= 3:
            model.is_available = False
            logger.warning("模型 %s 已标记为不可用（连续 %d 次失败）", model_id, model.failure_count)

    def report_success(self, model_id: str, input_tokens: int, output_tokens: int):
        """报告模型调用成功，记录用量."""
        model = self._models.get(model_id)
        if not model:
            return

        model.failure_count = 0  # 重置失败计数
        cost = (
            (input_tokens / 1000) * model.cost_per_1k_input
            + (output_tokens / 1000) * model.cost_per_1k_output
        )
        self._total_cost += cost
        self._usage_log.append({
            "model": model_id,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "timestamp": time.time(),
        })

    def estimate_cost(self, task_description: str, estimated_tokens: int = 5000) -> dict:
        """预估任务成本."""
        complexity = self.classify_task(task_description)
        model = self.select_model(complexity=complexity)
        input_cost = (estimated_tokens / 1000) * model.cost_per_1k_input
        output_cost = (estimated_tokens / 2 / 1000) * model.cost_per_1k_output
        return {
            "model": model.id,
            "complexity": complexity.value,
            "estimated_input_tokens": estimated_tokens,
            "estimated_output_tokens": estimated_tokens // 2,
            "estimated_cost": round(input_cost + output_cost, 4),
        }

    def get_stats(self) -> dict:
        """获取路由统计."""
        model_usage: dict[str, int] = {}
        for log in self._usage_log:
            model_usage[log["model"]] = model_usage.get(log["model"], 0) + 1

        return {
            "total_cost": round(self._total_cost, 4),
            "total_calls": len(self._usage_log),
            "model_usage": model_usage,
            "available_models": [
                {"id": m.id, "tier": m.tier, "available": m.is_available}
                for m in self._models.values()
            ],
        }


model_router = ModelRouter()
