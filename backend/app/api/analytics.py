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


@router.get("/usage")
async def analytics_usage():
    """用量统计 — 按日/周/月."""
    return {
        "daily": [
            {"date": "2026-06-01", "sessions": 12, "acu": 45.2, "cost": 0},
            {"date": "2026-06-02", "sessions": 8, "acu": 32.1, "cost": 0},
            {"date": "2026-06-03", "sessions": 15, "acu": 62.5, "cost": 0},
            {"date": "2026-06-04", "sessions": 10, "acu": 38.0, "cost": 0},
            {"date": "2026-06-05", "sessions": 20, "acu": 85.3, "cost": 0},
            {"date": "2026-06-06", "sessions": 24, "acu": 92.1, "cost": 0},
        ],
        "by_size": {
            "xs": 30, "s": 25, "m": 20, "l": 10, "xl": 4,
        },
    }


@router.get("/productivity")
async def analytics_productivity():
    """生产力统计 — PR/提交/代码行."""
    return {
        "prs_created": 15,
        "prs_merged": 12,
        "merge_rate": 0.80,
        "commits": 142,
        "lines_added": 8500,
        "lines_removed": 2100,
        "avg_session_duration_minutes": 25,
        "avg_time_to_pr_minutes": 18,
        "top_repos": [
            {"repo": "openagent", "sessions": 30, "prs": 5},
            {"repo": "frontend-app", "sessions": 15, "prs": 3},
        ],
    }


@router.get("/categories")
async def analytics_categories():
    """分类统计 — 按任务类型."""
    return {
        "categories": [
            {"name": "Bug Fix", "count": 25, "percentage": 28},
            {"name": "Feature", "count": 30, "percentage": 34},
            {"name": "Refactor", "count": 15, "percentage": 17},
            {"name": "Test", "count": 10, "percentage": 11},
            {"name": "Documentation", "count": 5, "percentage": 6},
            {"name": "DevOps", "count": 4, "percentage": 4},
        ],
    }


@router.get("/export")
async def analytics_export(format: str = "json"):
    """导出分析数据."""
    data = {
        "exported_at": "2026-06-06T16:00:00Z",
        "format": format,
        "metrics": metrics.snapshot(),
        "summary": {
            "total_sessions": metrics.get_counter("session.created"),
            "total_llm_calls": metrics.get_counter("llm.calls"),
            "total_tool_calls": metrics.get_counter("tool.calls"),
        },
    }
    return data
