"""可观测性 / Observability & Telemetry.

OpenTelemetry 追踪骨架 + Agent 操作指标收集。
参考行业标准: OpenTelemetry + GenAI 语义约定。
"""

from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 追踪 (Tracing) — 轻量骨架, Phase 2 接 OTel SDK
# ---------------------------------------------------------------------------


@dataclass
class Span:
    """追踪 Span (兼容 OTel 数据模型)."""

    name: str
    trace_id: str = ""
    span_id: str = ""
    parent_id: str = ""
    start_time: float = 0.0
    end_time: float = 0.0
    attributes: dict[str, Any] = field(default_factory=dict)
    status: str = "ok"  # ok / error
    events: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        import uuid

        if not self.trace_id:
            self.trace_id = uuid.uuid4().hex[:32]
        if not self.span_id:
            self.span_id = uuid.uuid4().hex[:16]
        if not self.start_time:
            self.start_time = time.time()

    def add_event(self, name: str, attributes: dict[str, Any] | None = None) -> None:
        self.events.append({
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {},
        })

    def finish(self, status: str = "ok") -> None:
        self.end_time = time.time()
        self.status = status

    @property
    def duration_ms(self) -> float:
        if not self.end_time:
            return (time.time() - self.start_time) * 1000
        return (self.end_time - self.start_time) * 1000

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms,
            "attributes": self.attributes,
            "status": self.status,
            "events": self.events,
        }


class Tracer:
    """轻量追踪器.

    Phase 1: 内存存储 + 日志输出
    Phase 2: 接 OTel Collector → Jaeger/Tempo
    """

    def __init__(self, service_name: str = "openagent") -> None:
        self.service_name = service_name
        self._spans: list[Span] = []
        self._max_spans = 10000

    @contextmanager
    def start_span(
        self,
        name: str,
        parent: Span | None = None,
        attributes: dict[str, Any] | None = None,
    ):
        """创建 Span 上下文管理器."""
        span = Span(
            name=name,
            parent_id=parent.span_id if parent else "",
            trace_id=parent.trace_id if parent else "",
            attributes=attributes or {},
        )
        try:
            yield span
            span.finish("ok")
        except Exception as e:
            span.finish("error")
            span.add_event("exception", {"message": str(e), "type": type(e).__name__})
            raise
        finally:
            self._record(span)

    def _record(self, span: Span) -> None:
        self._spans.append(span)
        if len(self._spans) > self._max_spans:
            self._spans = self._spans[-self._max_spans:]
        logger.debug(
            "span: %s duration=%.1fms status=%s",
            span.name,
            span.duration_ms,
            span.status,
        )

    def get_traces(self, limit: int = 100) -> list[dict[str, Any]]:
        """获取最近的追踪数据."""
        return [s.to_dict() for s in self._spans[-limit:]]


# ---------------------------------------------------------------------------
# 指标 (Metrics) — Agent 操作统计
# ---------------------------------------------------------------------------


@dataclass
class MetricsCollector:
    """Agent 操作指标收集器.

    收集: LLM 调用次数/延迟/token 消耗, 工具调用成功率, 沙箱使用率等。
    """

    counters: dict[str, int] = field(default_factory=dict)
    histograms: dict[str, list[float]] = field(default_factory=dict)

    def increment(self, name: str, value: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + value

    def record(self, name: str, value: float) -> None:
        if name not in self.histograms:
            self.histograms[name] = []
        hist = self.histograms[name]
        hist.append(value)
        if len(hist) > 10000:
            self.histograms[name] = hist[-10000:]

    def get_counter(self, name: str) -> int:
        return self.counters.get(name, 0)

    def get_histogram_stats(self, name: str) -> dict[str, float]:
        hist = self.histograms.get(name, [])
        if not hist:
            return {"count": 0, "mean": 0, "min": 0, "max": 0, "p99": 0}
        sorted_h = sorted(hist)
        n = len(sorted_h)
        return {
            "count": n,
            "mean": sum(sorted_h) / n,
            "min": sorted_h[0],
            "max": sorted_h[-1],
            "p99": sorted_h[min(int(n * 0.99), n - 1)],
        }

    def snapshot(self) -> dict[str, Any]:
        """全量指标快照."""
        return {
            "counters": dict(self.counters),
            "histograms": {
                name: self.get_histogram_stats(name)
                for name in self.histograms
            },
        }


# 全局单例
tracer = Tracer()
metrics = MetricsCollector()
