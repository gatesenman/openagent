"""Multi-Agent Collaboration Coordinator.

Implements the Coordinator pattern from planning docs:
- Coordinator Agent dispatches sub-tasks to specialized agents
- Code Agent, Review Agent, Test Agent collaborate
- Communication via A2A protocol
- Conflict resolution by Coordinator
- Saga compensation for failure handling
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class AgentRole(str, Enum):
    COORDINATOR = "coordinator"
    CODE = "code"
    REVIEW = "review"
    TEST = "test"
    PLAN = "plan"
    DEBUG = "debug"


class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class ConflictType(str, Enum):
    FILE_CONFLICT = "file_conflict"
    DESIGN_DISAGREEMENT = "design_disagreement"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    TEST_FAILURE = "test_failure"


@dataclass
class AgentMessage:
    """Message between agents."""

    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: str = ""
    to_agent: str = ""
    message_type: str = "info"  # info, request, response, alert, conflict
    content: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class SubTask:
    """A sub-task assigned to a specialized agent."""

    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parent_task_id: str = ""
    description: str = ""
    assigned_to: AgentRole = AgentRole.CODE
    status: TaskStatus = TaskStatus.PENDING
    depends_on: list[str] = field(default_factory=list)
    files_involved: list[str] = field(default_factory=list)
    result: dict[str, Any] = field(default_factory=dict)
    error: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    completed_at: str = ""


@dataclass
class CollaborationSession:
    """A multi-agent collaboration session."""

    session_id: str
    coordinator_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agents: dict[str, AgentRole] = field(default_factory=dict)
    tasks: list[SubTask] = field(default_factory=list)
    messages: list[AgentMessage] = field(default_factory=list)
    conflicts: list[dict[str, Any]] = field(default_factory=list)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class MultiAgentCoordinator:
    """Coordinator for multi-agent collaboration.

    Workflow:
    1. User task -> Coordinator decomposes into sub-tasks
    2. Sub-tasks assigned to specialized agents (Code/Review/Test)
    3. Agents execute and communicate via messages
    4. Coordinator resolves conflicts and merges results
    5. Failed tasks trigger Saga compensation
    """

    def __init__(self) -> None:
        self._sessions: dict[str, CollaborationSession] = {}

    def create_session(self, session_id: str) -> CollaborationSession:
        """Create a new multi-agent collaboration session."""
        session = CollaborationSession(session_id=session_id)

        # Register default agents
        session.agents = {
            "coordinator": AgentRole.COORDINATOR,
            "code_agent": AgentRole.CODE,
            "review_agent": AgentRole.REVIEW,
            "test_agent": AgentRole.TEST,
        }

        self._sessions[session_id] = session
        return session

    def decompose_task(
        self, session_id: str, task_description: str
    ) -> list[SubTask]:
        """Decompose a user task into sub-tasks for different agents.

        In production: uses LLM to analyze task and create sub-tasks
        with proper dependency ordering.
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Create standard sub-task pipeline
        plan_task = SubTask(
            description=f"Analyze and plan: {task_description}",
            assigned_to=AgentRole.PLAN,
        )

        code_task = SubTask(
            description=f"Implement: {task_description}",
            assigned_to=AgentRole.CODE,
            depends_on=[plan_task.task_id],
        )

        review_task = SubTask(
            description=f"Review code changes for: {task_description}",
            assigned_to=AgentRole.REVIEW,
            depends_on=[code_task.task_id],
        )

        test_task = SubTask(
            description=f"Write and run tests for: {task_description}",
            assigned_to=AgentRole.TEST,
            depends_on=[code_task.task_id],
        )

        tasks = [plan_task, code_task, review_task, test_task]
        session.tasks.extend(tasks)
        return tasks

    def assign_task(
        self, session_id: str, task_id: str, agent_role: AgentRole
    ) -> SubTask | None:
        """Assign a sub-task to a specific agent role."""
        session = self._sessions.get(session_id)
        if not session:
            return None

        for task in session.tasks:
            if task.task_id == task_id:
                task.assigned_to = agent_role
                task.status = TaskStatus.ASSIGNED
                return task
        return None

    def update_task_status(
        self,
        session_id: str,
        task_id: str,
        status: TaskStatus,
        result: dict[str, Any] | None = None,
        error: str = "",
    ) -> SubTask | None:
        """Update task status (called by agents as they progress)."""
        session = self._sessions.get(session_id)
        if not session:
            return None

        for task in session.tasks:
            if task.task_id == task_id:
                task.status = status
                if result:
                    task.result = result
                if error:
                    task.error = error
                if status == TaskStatus.COMPLETED:
                    task.completed_at = datetime.now(timezone.utc).isoformat()
                return task
        return None

    def send_message(
        self,
        session_id: str,
        from_agent: str,
        to_agent: str,
        message_type: str,
        content: str,
        data: dict[str, Any] | None = None,
    ) -> AgentMessage:
        """Send a message between agents."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        msg = AgentMessage(
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            data=data or {},
        )
        session.messages.append(msg)
        return msg

    def report_conflict(
        self,
        session_id: str,
        conflict_type: ConflictType,
        description: str,
        agents_involved: list[str],
    ) -> dict[str, Any]:
        """Report a conflict between agents for Coordinator resolution."""
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        conflict = {
            "conflict_id": str(uuid.uuid4()),
            "type": conflict_type.value,
            "description": description,
            "agents_involved": agents_involved,
            "resolution": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        session.conflicts.append(conflict)
        return conflict

    def resolve_conflict(
        self, session_id: str, conflict_id: str, resolution: str
    ) -> bool:
        """Coordinator resolves a reported conflict."""
        session = self._sessions.get(session_id)
        if not session:
            return False

        for conflict in session.conflicts:
            if conflict["conflict_id"] == conflict_id:
                conflict["resolution"] = resolution
                return True
        return False

    def get_ready_tasks(self, session_id: str) -> list[SubTask]:
        """Get tasks whose dependencies are all completed."""
        session = self._sessions.get(session_id)
        if not session:
            return []

        completed_ids = {
            t.task_id for t in session.tasks if t.status == TaskStatus.COMPLETED
        }

        return [
            t
            for t in session.tasks
            if t.status == TaskStatus.PENDING
            and all(dep in completed_ids for dep in t.depends_on)
        ]

    def compensate_failure(self, session_id: str, failed_task_id: str) -> list[str]:
        """Saga compensation: rollback dependent tasks when one fails.

        Returns list of task IDs that were cancelled.
        """
        session = self._sessions.get(session_id)
        if not session:
            return []

        cancelled = []
        # Cancel all tasks that depend on the failed task
        for task in session.tasks:
            if failed_task_id in task.depends_on and task.status in (
                TaskStatus.PENDING,
                TaskStatus.ASSIGNED,
            ):
                task.status = TaskStatus.CANCELLED
                cancelled.append(task.task_id)

        return cancelled

    def get_session_status(self, session_id: str) -> dict[str, Any]:
        """Get overall collaboration session status."""
        session = self._sessions.get(session_id)
        if not session:
            return {}

        status_counts: dict[str, int] = {}
        for task in session.tasks:
            status_counts[task.status.value] = (
                status_counts.get(task.status.value, 0) + 1
            )

        return {
            "session_id": session_id,
            "total_tasks": len(session.tasks),
            "status_counts": status_counts,
            "total_messages": len(session.messages),
            "unresolved_conflicts": sum(
                1 for c in session.conflicts if not c.get("resolution")
            ),
            "agents": {k: v.value for k, v in session.agents.items()},
        }


# Singleton
multi_agent_coordinator = MultiAgentCoordinator()
