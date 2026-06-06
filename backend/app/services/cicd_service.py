"""CI/CD 集成服务 / CI/CD Integration Service.

支持:
- GitHub Actions 集成
- GitLab CI 集成
- 自定义 Pipeline
- PR 状态同步
- CI 结果反馈到 Agent
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class CIProvider(str, Enum):
    GITHUB_ACTIONS = "github_actions"
    GITLAB_CI = "gitlab_ci"
    CUSTOM = "custom"


class PipelineStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"
    CANCELLED = "cancelled"


@dataclass
class PipelineStep:
    """流水线步骤."""
    name: str = ""
    status: PipelineStatus = PipelineStatus.PENDING
    command: str = ""
    output: str = ""
    duration_ms: int = 0
    exit_code: int = -1


@dataclass
class Pipeline:
    """CI/CD 流水线."""
    id: str = ""
    session_id: str = ""
    provider: CIProvider = CIProvider.GITHUB_ACTIONS
    repo_url: str = ""
    branch: str = ""
    commit_sha: str = ""
    status: PipelineStatus = PipelineStatus.PENDING
    steps: list[PipelineStep] = field(default_factory=list)
    pr_number: int = 0
    triggered_at: float = 0.0
    completed_at: float = 0.0
    logs_url: str = ""

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.triggered_at:
            self.triggered_at = time.time()


class CICDService:
    """CI/CD 集成服务."""

    def __init__(self):
        self._pipelines: dict[str, Pipeline] = {}
        self._templates: dict[str, list[dict]] = {
            "python": [
                {"name": "lint", "command": "ruff check ."},
                {"name": "typecheck", "command": "mypy ."},
                {"name": "test", "command": "pytest tests/ -v"},
                {"name": "build", "command": "python -m build"},
            ],
            "node": [
                {"name": "lint", "command": "npm run lint"},
                {"name": "typecheck", "command": "npm run typecheck"},
                {"name": "test", "command": "npm test"},
                {"name": "build", "command": "npm run build"},
            ],
            "fullstack": [
                {"name": "backend-lint", "command": "cd backend && ruff check ."},
                {"name": "backend-test", "command": "cd backend && pytest tests/ -v"},
                {"name": "frontend-lint", "command": "cd frontend && npm run lint"},
                {"name": "frontend-build", "command": "cd frontend && npm run build"},
            ],
        }

    def create_pipeline(
        self,
        session_id: str,
        provider: str = "github_actions",
        repo_url: str = "",
        branch: str = "main",
        commit_sha: str = "",
        template: str = "",
    ) -> Pipeline:
        """创建流水线."""
        pipeline = Pipeline(
            session_id=session_id,
            provider=CIProvider(provider),
            repo_url=repo_url,
            branch=branch,
            commit_sha=commit_sha,
        )

        # 使用模板创建步骤
        if template and template in self._templates:
            for step_def in self._templates[template]:
                pipeline.steps.append(PipelineStep(
                    name=step_def["name"],
                    command=step_def["command"],
                ))

        self._pipelines[pipeline.id] = pipeline
        return pipeline

    def run_pipeline(self, pipeline_id: str) -> Pipeline | None:
        """运行流水线 (Phase 1: 模拟执行, Phase 2: 实际在沙箱中执行)."""
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return None
        pipeline.status = PipelineStatus.RUNNING

        # Phase 1: 模拟步骤执行
        all_passed = True
        for step in pipeline.steps:
            step.status = PipelineStatus.SUCCESS
            step.exit_code = 0
            step.duration_ms = 1000
            step.output = f"[模拟] {step.command} 执行成功"

        pipeline.status = PipelineStatus.SUCCESS if all_passed else PipelineStatus.FAILURE
        pipeline.completed_at = time.time()
        return pipeline

    def update_step(
        self, pipeline_id: str, step_name: str,
        status: str, output: str = "", exit_code: int = 0
    ) -> bool:
        """更新步骤状态."""
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return False
        for step in pipeline.steps:
            if step.name == step_name:
                step.status = PipelineStatus(status)
                step.output = output
                step.exit_code = exit_code
                return True
        return False

    def get_pipeline(self, pipeline_id: str) -> dict | None:
        """获取流水线详情."""
        p = self._pipelines.get(pipeline_id)
        if not p:
            return None
        return {
            "id": p.id,
            "session_id": p.session_id,
            "provider": p.provider.value,
            "repo_url": p.repo_url,
            "branch": p.branch,
            "commit_sha": p.commit_sha,
            "status": p.status.value,
            "pr_number": p.pr_number,
            "steps": [
                {
                    "name": s.name,
                    "status": s.status.value,
                    "command": s.command,
                    "output": s.output[:500],
                    "duration_ms": s.duration_ms,
                    "exit_code": s.exit_code,
                }
                for s in p.steps
            ],
            "triggered_at": p.triggered_at,
            "completed_at": p.completed_at,
        }

    def list_pipelines(self, session_id: str = "") -> list[dict]:
        """列出流水线."""
        results = []
        for p in self._pipelines.values():
            if session_id and p.session_id != session_id:
                continue
            results.append({
                "id": p.id,
                "status": p.status.value,
                "provider": p.provider.value,
                "branch": p.branch,
                "triggered_at": p.triggered_at,
            })
        return results

    def get_templates(self) -> dict:
        """获取流水线模板."""
        return self._templates


cicd_service = CICDService()
