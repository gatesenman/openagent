"""Evaluation API — Agent benchmark and evaluation endpoints."""

from fastapi import APIRouter

from app.agent.evaluation import BenchmarkType, agent_evaluator

router = APIRouter()


@router.get("/cases")
async def list_eval_cases(benchmark: str | None = None):
    """List available evaluation cases."""
    btype = BenchmarkType(benchmark) if benchmark else None
    return {"cases": agent_evaluator.list_cases(btype)}


@router.post("/run/{case_id}")
async def run_eval_case(case_id: str):
    """Run a single evaluation case."""
    run = await agent_evaluator.run_evaluation(case_id)
    return {
        "case_id": run.case_id,
        "result": run.result.value,
        "total_tokens": run.total_tokens,
        "duration_seconds": run.duration_seconds,
    }


@router.post("/suite")
async def run_eval_suite(benchmark: str | None = None, tags: list[str] | None = None):
    """Run evaluation suite."""
    btype = BenchmarkType(benchmark) if benchmark else None
    runs = await agent_evaluator.run_suite(btype, tags)
    return {
        "total_runs": len(runs),
        "results": [
            {"case_id": r.case_id, "result": r.result.value} for r in runs
        ],
    }


@router.get("/summary")
async def get_eval_summary():
    """Get aggregate evaluation summary."""
    return agent_evaluator.get_summary()
