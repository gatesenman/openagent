"""调度服务 — 定时任务和一次性会话调度."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class ScheduleType(Enum):
    cron = "cron"
    once = "once"
    interval = "interval"


class ScheduleStatus(Enum):
    active = "active"
    paused = "paused"
    completed = "completed"
    failed = "failed"


@dataclass
class ScheduleRun:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    schedule_id: str = ""
    session_id: str = ""
    status: str = "pending"
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: str = ""


@dataclass
class Schedule:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    org_id: str = ""
    name: str = ""
    description: str = ""
    schedule_type: ScheduleType = ScheduleType.cron
    cron_expression: str = ""
    interval_minutes: int = 0
    run_at: Optional[str] = None
    prompt: str = ""
    model: str = "auto"
    mode: str = "localhost"
    playbook_id: str = ""
    repo_url: str = ""
    status: ScheduleStatus = ScheduleStatus.active
    max_runs: int = 0
    runs: list = field(default_factory=list)
    last_run_at: Optional[str] = None
    next_run_at: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class ScheduleService:
    def __init__(self):
        self._schedules: dict[str, Schedule] = {}

    def create_schedule(
        self,
        org_id: str,
        name: str,
        prompt: str,
        schedule_type: str = "cron",
        cron_expression: str = "",
        interval_minutes: int = 0,
        run_at: str = "",
        model: str = "auto",
        mode: str = "localhost",
        playbook_id: str = "",
        repo_url: str = "",
        max_runs: int = 0,
        description: str = "",
    ) -> Schedule:
        sched = Schedule(
            org_id=org_id,
            name=name,
            description=description,
            prompt=prompt,
            schedule_type=ScheduleType(schedule_type),
            cron_expression=cron_expression,
            interval_minutes=interval_minutes,
            run_at=run_at or None,
            model=model,
            mode=mode,
            playbook_id=playbook_id,
            repo_url=repo_url,
            max_runs=max_runs,
        )
        self._schedules[sched.id] = sched
        return sched

    def get_schedule(self, schedule_id: str) -> Optional[dict]:
        s = self._schedules.get(schedule_id)
        if not s:
            return None
        return {
            "id": s.id,
            "org_id": s.org_id,
            "name": s.name,
            "description": s.description,
            "schedule_type": s.schedule_type.value,
            "cron_expression": s.cron_expression,
            "interval_minutes": s.interval_minutes,
            "run_at": s.run_at,
            "prompt": s.prompt,
            "model": s.model,
            "mode": s.mode,
            "status": s.status.value,
            "max_runs": s.max_runs,
            "total_runs": len(s.runs),
            "last_run_at": s.last_run_at,
            "next_run_at": s.next_run_at,
            "created_at": s.created_at,
        }

    def list_schedules(self, org_id: str = "") -> list[dict]:
        results = []
        for s in self._schedules.values():
            if org_id and s.org_id != org_id:
                continue
            results.append({
                "id": s.id,
                "name": s.name,
                "schedule_type": s.schedule_type.value,
                "status": s.status.value,
                "total_runs": len(s.runs),
                "last_run_at": s.last_run_at,
                "next_run_at": s.next_run_at,
                "created_at": s.created_at,
            })
        return results

    def trigger_run(self, schedule_id: str) -> Optional[ScheduleRun]:
        s = self._schedules.get(schedule_id)
        if not s:
            return None
        run = ScheduleRun(
            schedule_id=schedule_id,
            session_id=str(uuid.uuid4()),
            status="running",
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        # Phase 1: 模拟执行
        run.status = "completed"
        run.completed_at = datetime.now(timezone.utc).isoformat()
        run.result = "Session completed successfully"
        s.runs.append(run)
        s.last_run_at = run.completed_at
        return run

    def pause_schedule(self, schedule_id: str) -> bool:
        s = self._schedules.get(schedule_id)
        if not s:
            return False
        s.status = ScheduleStatus.paused
        return True

    def resume_schedule(self, schedule_id: str) -> bool:
        s = self._schedules.get(schedule_id)
        if not s:
            return False
        s.status = ScheduleStatus.active
        return True

    def delete_schedule(self, schedule_id: str) -> bool:
        if schedule_id in self._schedules:
            del self._schedules[schedule_id]
            return True
        return False

    def get_runs(self, schedule_id: str) -> list[dict]:
        s = self._schedules.get(schedule_id)
        if not s:
            return []
        return [
            {
                "id": r.id,
                "session_id": r.session_id,
                "status": r.status,
                "started_at": r.started_at,
                "completed_at": r.completed_at,
                "result": r.result,
            }
            for r in s.runs
        ]


schedule_service = ScheduleService()
