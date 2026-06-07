"""Agent Evaluation & Benchmark Framework.

Provides structured evaluation of Agent performance across
multiple dimensions: task completion, code quality, hallucination,
token efficiency, and time-to-PR.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class BenchmarkType(str, Enum):
    SWE_BENCH = "swe_bench"
    CODE_GENERATION = "code_generation"
    BUG_FIX = "bug_fix"
    REFACTOR = "refactor"
    TEST_WRITING = "test_writing"
    CODE_REVIEW = "code_review"
    CUSTOM = "custom"


class EvalResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    PARTIAL = "partial"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class EvalDimension:
    """A single evaluation dimension with target and actual score."""

    name: str
    description: str
    target: float
    actual: float = 0.0
    weight: float = 1.0
    unit: str = "%"

    @property
    def passed(self) -> bool:
        return self.actual >= self.target

    @property
    def score(self) -> float:
        return min(self.actual / self.target, 1.0) * self.weight if self.target > 0 else 0.0


@dataclass
class EvalCase:
    """A single evaluation test case."""

    case_id: str
    benchmark: BenchmarkType
    description: str
    input_prompt: str
    expected_output: str | None = None
    expected_files: list[str] = field(default_factory=list)
    expected_tests_pass: bool = True
    timeout_seconds: int = 600
    tags: list[str] = field(default_factory=list)


@dataclass
class EvalRun:
    """Result of running an evaluation case."""

    case_id: str
    result: EvalResult
    dimensions: dict[str, EvalDimension] = field(default_factory=dict)
    total_tokens: int = 0
    total_tool_calls: int = 0
    total_llm_calls: int = 0
    duration_seconds: float = 0.0
    errors: list[str] = field(default_factory=list)
    agent_actions: list[dict[str, Any]] = field(default_factory=list)
    started_at: str = ""
    completed_at: str = ""


class AgentEvaluator:
    """Evaluates Agent performance across multiple benchmarks.

    Dimensions (from planning doc):
    - task_completion_rate: >80%
    - code_quality_score: >95%
    - hallucination_rate: <5%
    - token_efficiency: <50K tokens/task
    - first_try_success: >60%
    - time_to_pr: <10min (simple tasks)
    - user_intervention_rate: <30%
    """

    STANDARD_DIMENSIONS = {
        "task_completion": EvalDimension(
            name="task_completion",
            description="Agent successfully completes user tasks",
            target=80.0,
            unit="%",
            weight=1.5,
        ),
        "code_quality": EvalDimension(
            name="code_quality",
            description="Generated code passes lint + type checks",
            target=95.0,
            unit="%",
            weight=1.2,
        ),
        "hallucination_rate": EvalDimension(
            name="hallucination_rate",
            description="Rate of false claims (lower is better)",
            target=5.0,
            unit="% (inverse)",
            weight=1.3,
        ),
        "token_efficiency": EvalDimension(
            name="token_efficiency",
            description="Average tokens per successful task",
            target=50000,
            unit="tokens",
            weight=0.8,
        ),
        "first_try_success": EvalDimension(
            name="first_try_success",
            description="Tasks completed without user intervention",
            target=60.0,
            unit="%",
            weight=1.0,
        ),
        "time_to_pr": EvalDimension(
            name="time_to_pr",
            description="Average time from task to PR creation",
            target=600,
            unit="seconds",
            weight=0.7,
        ),
    }

    def __init__(self) -> None:
        self._cases: dict[str, EvalCase] = {}
        self._runs: list[EvalRun] = []
        self._load_builtin_cases()

    def _load_builtin_cases(self) -> None:
        """Load built-in evaluation cases."""
        builtins = [
            EvalCase(
                case_id="eval-001",
                benchmark=BenchmarkType.BUG_FIX,
                description="Fix off-by-one error in pagination",
                input_prompt="Fix the pagination bug: page 2 shows same results as page 1",
                expected_files=["src/utils/pagination.py"],
                tags=["bug-fix", "easy"],
            ),
            EvalCase(
                case_id="eval-002",
                benchmark=BenchmarkType.CODE_GENERATION,
                description="Add JWT authentication middleware",
                input_prompt="Add JWT auth middleware to the Express API",
                expected_files=["src/middleware/auth.ts"],
                tags=["feature", "medium"],
            ),
            EvalCase(
                case_id="eval-003",
                benchmark=BenchmarkType.TEST_WRITING,
                description="Write unit tests for user service",
                input_prompt="Write comprehensive tests for UserService",
                expected_tests_pass=True,
                tags=["testing", "medium"],
            ),
            EvalCase(
                case_id="eval-004",
                benchmark=BenchmarkType.REFACTOR,
                description="Extract common DB logic into base repository",
                input_prompt="Refactor: extract shared CRUD operations into BaseRepository",
                tags=["refactor", "hard"],
            ),
            EvalCase(
                case_id="eval-005",
                benchmark=BenchmarkType.CODE_REVIEW,
                description="Review PR for security issues",
                input_prompt="Review this PR and identify security vulnerabilities",
                tags=["review", "security"],
            ),
        ]
        for case in builtins:
            self._cases[case.case_id] = case

    def register_case(self, case: EvalCase) -> None:
        """Register a custom evaluation case."""
        self._cases[case.case_id] = case

    async def run_evaluation(self, case_id: str) -> EvalRun:
        """Run a single evaluation case and return results."""
        case = self._cases.get(case_id)
        if not case:
            raise ValueError(f"Eval case {case_id} not found")

        started = datetime.now(timezone.utc)
        run = EvalRun(
            case_id=case_id,
            result=EvalResult.PASS,
            started_at=started.isoformat(),
            dimensions={k: EvalDimension(**{
                "name": v.name,
                "description": v.description,
                "target": v.target,
                "weight": v.weight,
                "unit": v.unit,
            }) for k, v in self.STANDARD_DIMENSIONS.items()},
        )

        # In production: actually run the Agent on the case
        # For now: return structured skeleton
        run.completed_at = datetime.now(timezone.utc).isoformat()
        self._runs.append(run)
        return run

    async def run_suite(
        self, benchmark: BenchmarkType | None = None, tags: list[str] | None = None
    ) -> list[EvalRun]:
        """Run all matching evaluation cases."""
        cases = list(self._cases.values())
        if benchmark:
            cases = [c for c in cases if c.benchmark == benchmark]
        if tags:
            cases = [c for c in cases if any(t in c.tags for t in tags)]

        results = []
        for case in cases:
            run = await self.run_evaluation(case.case_id)
            results.append(run)
        return results

    def get_summary(self) -> dict[str, Any]:
        """Get aggregate evaluation summary."""
        if not self._runs:
            return {"total_runs": 0, "dimensions": {}}

        total = len(self._runs)
        passed = sum(1 for r in self._runs if r.result == EvalResult.PASS)

        return {
            "total_runs": total,
            "passed": passed,
            "pass_rate": round(passed / total * 100, 1) if total else 0,
            "avg_tokens": (
                round(sum(r.total_tokens for r in self._runs) / total)
                if total
                else 0
            ),
            "avg_duration": (
                round(sum(r.duration_seconds for r in self._runs) / total, 1)
                if total
                else 0
            ),
        }

    def list_cases(
        self, benchmark: BenchmarkType | None = None
    ) -> list[dict[str, Any]]:
        """List available evaluation cases."""
        cases = list(self._cases.values())
        if benchmark:
            cases = [c for c in cases if c.benchmark == benchmark]
        return [
            {
                "case_id": c.case_id,
                "benchmark": c.benchmark.value,
                "description": c.description,
                "tags": c.tags,
            }
            for c in cases
        ]


# Singleton
agent_evaluator = AgentEvaluator()
