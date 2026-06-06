"""任务规划器 / Task planner.

将用户任务分解为可执行的步骤计划。
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class TaskStep:
    """任务步骤."""
    id: int
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    tools_needed: list[str] = field(default_factory=list)
    dependencies: list[int] = field(default_factory=list)
    result: str | None = None


@dataclass
class TaskPlan:
    """任务计划."""
    goal: str
    steps: list[TaskStep] = field(default_factory=list)
    current_step: int = 0
    total_steps: int = 0

    def to_dict(self) -> dict:
        return {
            "goal": self.goal,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "steps": [
                {
                    "id": s.id,
                    "title": s.title,
                    "description": s.description,
                    "status": s.status.value,
                    "tools_needed": s.tools_needed,
                }
                for s in self.steps
            ],
        }

    def next_step(self) -> TaskStep | None:
        """获取下一个待执行的步骤."""
        for step in self.steps:
            if step.status == TaskStatus.PENDING:
                # 检查依赖是否完成
                deps_met = all(
                    self.steps[d - 1].status == TaskStatus.COMPLETED
                    for d in step.dependencies
                    if d <= len(self.steps)
                )
                if deps_met:
                    return step
        return None

    def mark_completed(self, step_id: int, result: str = "") -> None:
        """标记步骤完成."""
        for step in self.steps:
            if step.id == step_id:
                step.status = TaskStatus.COMPLETED
                step.result = result
                self.current_step = step_id
                break

    def mark_failed(self, step_id: int, error: str = "") -> None:
        """标记步骤失败."""
        for step in self.steps:
            if step.id == step_id:
                step.status = TaskStatus.FAILED
                step.result = error
                break


class TaskPlanner:
    """任务规划器.

    使用 LLM 将用户的自然语言任务分解为结构化步骤。
    如果没有 LLM，使用规则引擎生成基本计划。
    """

    async def create_plan(
        self,
        task: str,
        context: str = "",
        llm_client: Any = None,
        model: str = "gpt-4o",
    ) -> TaskPlan:
        """创建任务计划.

        Args:
            task: 用户任务描述
            context: 额外上下文（仓库信息、文件列表等）
            llm_client: LLM 客户端（可选）
            model: LLM 模型
        """
        if llm_client:
            return await self._plan_with_llm(task, context, llm_client, model)
        return self._plan_with_rules(task)

    async def _plan_with_llm(
        self, task: str, context: str, llm_client: Any, model: str
    ) -> TaskPlan:
        """使用 LLM 生成计划."""
        prompt = f"""将以下任务分解为可执行的步骤。

任务: {task}

{f"上下文: {context}" if context else ""}

以 JSON 格式返回:
{{
    "goal": "任务目标摘要",
    "steps": [
        {{
            "id": 1,
            "title": "步骤标题",
            "description": "详细描述",
            "tools_needed": ["shell_exec", "file_read"],
            "dependencies": []
        }}
    ]
}}"""

        try:
            response = await llm_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.1,
            )
            data = json.loads(response.choices[0].message.content)
            plan = TaskPlan(
                goal=data.get("goal", task),
                total_steps=len(data.get("steps", [])),
            )
            for s in data.get("steps", []):
                plan.steps.append(TaskStep(
                    id=s["id"],
                    title=s["title"],
                    description=s.get("description", ""),
                    tools_needed=s.get("tools_needed", []),
                    dependencies=s.get("dependencies", []),
                ))
            return plan
        except Exception as e:
            logger.warning("LLM 规划失败，降级为规则引擎: %s", e)
            return self._plan_with_rules(task)

    def _plan_with_rules(self, task: str) -> TaskPlan:
        """规则引擎生成基本计划（降级方案）."""
        steps = [
            TaskStep(
                id=1,
                title="分析任务",
                description="理解任务需求，确定工作范围",
                tools_needed=[],
            ),
            TaskStep(
                id=2,
                title="探索代码库",
                description="了解项目结构和相关文件",
                tools_needed=["shell_exec", "file_read", "search_code"],
                dependencies=[1],
            ),
            TaskStep(
                id=3,
                title="实施修改",
                description="按需求修改或创建代码",
                tools_needed=["file_write", "file_read"],
                dependencies=[2],
            ),
            TaskStep(
                id=4,
                title="验证结果",
                description="测试修改是否正确",
                tools_needed=["shell_exec"],
                dependencies=[3],
            ),
        ]

        return TaskPlan(goal=task, steps=steps, total_steps=len(steps))
