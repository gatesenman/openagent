"""任务分解与并行子Agent / Task decomposition & parallel sub-agents.

支持:
- 大任务自动拆解为子任务
- 子Agent并行执行（各自独立沙箱）
- 结果汇总和冲突解决
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SubTask:
    """子任务."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: list[str] = field(default_factory=list)
    assigned_agent: str | None = None
    result: dict | None = None
    files_changed: list[str] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "dependencies": self.dependencies,
            "assigned_agent": self.assigned_agent,
            "result": self.result,
            "files_changed": self.files_changed,
            "error": self.error,
        }


@dataclass
class TaskPlan:
    """任务执行计划."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    goal: str = ""
    subtasks: list[SubTask] = field(default_factory=list)
    parallel_groups: list[list[str]] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "goal": self.goal,
            "subtasks": [t.to_dict() for t in self.subtasks],
            "parallel_groups": self.parallel_groups,
            "status": self.status.value,
            "total": len(self.subtasks),
            "completed": sum(1 for t in self.subtasks if t.status == TaskStatus.COMPLETED),
            "failed": sum(1 for t in self.subtasks if t.status == TaskStatus.FAILED),
        }


class TaskPlanner:
    """任务规划器.

    将大任务分解为可并行的子任务，
    构建依赖图，确定执行顺序。
    """

    def decompose(self, goal: str, context: dict | None = None) -> TaskPlan:
        """将目标分解为子任务.

        Phase 1: 基于模板的分解
        Phase 2: LLM 驱动的智能分解
        """
        plan = TaskPlan(goal=goal)

        # 根据目标类型模板化分解
        if any(kw in goal.lower() for kw in ["功能", "feature", "实现", "开发"]):
            plan.subtasks = self._feature_tasks(goal)
        elif any(kw in goal.lower() for kw in ["bug", "修复", "fix"]):
            plan.subtasks = self._bugfix_tasks(goal)
        elif any(kw in goal.lower() for kw in ["重构", "refactor"]):
            plan.subtasks = self._refactor_tasks(goal)
        elif any(kw in goal.lower() for kw in ["测试", "test"]):
            plan.subtasks = self._test_tasks(goal)
        else:
            plan.subtasks = self._generic_tasks(goal)

        plan.parallel_groups = self._build_parallel_groups(plan.subtasks)
        return plan

    def _feature_tasks(self, goal: str) -> list[SubTask]:
        return [
            SubTask(title="需求分析", description="解析需求，确定范围和依赖", priority=TaskPriority.HIGH),
            SubTask(title="API设计", description="设计接口定义、数据模型", priority=TaskPriority.HIGH),
            SubTask(title="后端实现", description="实现服务层和API端点", priority=TaskPriority.HIGH),
            SubTask(title="前端实现", description="实现UI组件和页面", priority=TaskPriority.HIGH),
            SubTask(title="编写测试", description="单元测试 + 集成测试", priority=TaskPriority.MEDIUM),
            SubTask(title="联调验证", description="端到端验证", priority=TaskPriority.MEDIUM),
        ]

    def _bugfix_tasks(self, goal: str) -> list[SubTask]:
        return [
            SubTask(title="复现Bug", description="在沙箱中复现问题", priority=TaskPriority.HIGH),
            SubTask(title="定位根因", description="分析日志和代码，定位根因", priority=TaskPriority.HIGH),
            SubTask(title="编写修复", description="实现修复代码", priority=TaskPriority.HIGH),
            SubTask(title="回归测试", description="编写和运行回归测试", priority=TaskPriority.MEDIUM),
        ]

    def _refactor_tasks(self, goal: str) -> list[SubTask]:
        return [
            SubTask(title="代码分析", description="度量复杂度、重复率、耦合度", priority=TaskPriority.HIGH),
            SubTask(title="确认测试覆盖", description="确保重构前有充分测试", priority=TaskPriority.HIGH),
            SubTask(title="逐步重构", description="每步保持可编译、测试通过", priority=TaskPriority.HIGH),
            SubTask(title="验证行为不变", description="运行完整测试套件", priority=TaskPriority.MEDIUM),
        ]

    def _test_tasks(self, goal: str) -> list[SubTask]:
        return [
            SubTask(title="分析代码结构", description="识别需要测试的函数和分支", priority=TaskPriority.HIGH),
            SubTask(title="生成单元测试", description="正常/边界/异常用例", priority=TaskPriority.HIGH),
            SubTask(title="生成集成测试", description="API和服务交互测试", priority=TaskPriority.MEDIUM),
            SubTask(title="运行并检查覆盖率", description="确保覆盖率 > 80%", priority=TaskPriority.MEDIUM),
        ]

    def _generic_tasks(self, goal: str) -> list[SubTask]:
        return [
            SubTask(title="分析任务", description="理解任务要求", priority=TaskPriority.HIGH),
            SubTask(title="执行任务", description="完成主要工作", priority=TaskPriority.HIGH),
            SubTask(title="验证结果", description="检查执行结果", priority=TaskPriority.MEDIUM),
        ]

    def _build_parallel_groups(self, tasks: list[SubTask]) -> list[list[str]]:
        """构建并行执行组.

        无依赖的任务可以并行执行。
        """
        groups = []
        remaining = set(t.id for t in tasks)
        completed = set()

        while remaining:
            group = []
            for task in tasks:
                if task.id in remaining:
                    deps = set(task.dependencies)
                    if deps.issubset(completed):
                        group.append(task.id)
            if not group:
                # 防止死循环
                group = list(remaining)[:1]
            groups.append(group)
            for tid in group:
                remaining.discard(tid)
                completed.add(tid)

        return groups

    async def execute_plan(
        self,
        plan: TaskPlan,
        execute_fn: Any = None,
    ) -> TaskPlan:
        """按并行组执行计划."""
        plan.status = TaskStatus.IN_PROGRESS
        task_map = {t.id: t for t in plan.subtasks}

        for group in plan.parallel_groups:
            tasks = [task_map[tid] for tid in group]
            for t in tasks:
                t.status = TaskStatus.IN_PROGRESS

            if execute_fn:
                results = await asyncio.gather(
                    *[execute_fn(t) for t in tasks],
                    return_exceptions=True,
                )
                for t, result in zip(tasks, results):
                    if isinstance(result, Exception):
                        t.status = TaskStatus.FAILED
                        t.error = str(result)
                    else:
                        t.status = TaskStatus.COMPLETED
                        t.result = result
            else:
                for t in tasks:
                    t.status = TaskStatus.COMPLETED

        all_done = all(t.status == TaskStatus.COMPLETED for t in plan.subtasks)
        plan.status = TaskStatus.COMPLETED if all_done else TaskStatus.FAILED
        return plan


task_planner = TaskPlanner()
