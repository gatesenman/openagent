"""分析与指标 API / Analytics & Metrics endpoints.

参考 Devin 的 Analytics 页面: 用量/生产力/分类统计。
"""

from fastapi import APIRouter

from app.core.telemetry import metrics, tracer

router = APIRouter()


@router.get("/metrics")
async def get_metrics():
    """获取系统指标快照."""
    return metrics.snapshot()


@router.get("/traces")
async def get_traces(limit: int = 50):
    """获取最近的追踪数据."""
    return {
        "traces": tracer.get_traces(limit),
        "total": len(tracer._spans),
    }


@router.get("/overview")
async def analytics_overview():
    """分析概览 — 仪表盘数据."""
    return {
        "llm": {
            "total_calls": metrics.get_counter("llm.calls"),
            "total_tokens": metrics.get_counter("llm.tokens"),
            "errors": metrics.get_counter("llm.errors"),
            "latency": metrics.get_histogram_stats("llm.latency_ms"),
        },
        "tools": {
            "total_calls": metrics.get_counter("tool.calls"),
            "successes": metrics.get_counter("tool.successes"),
            "failures": metrics.get_counter("tool.failures"),
            "latency": metrics.get_histogram_stats("tool.latency_ms"),
        },
        "sandbox": {
            "created": metrics.get_counter("sandbox.created"),
            "destroyed": metrics.get_counter("sandbox.destroyed"),
            "exec_count": metrics.get_counter("sandbox.exec"),
        },
        "sessions": {
            "total": metrics.get_counter("session.created"),
            "completed": metrics.get_counter("session.completed"),
        },
    }
