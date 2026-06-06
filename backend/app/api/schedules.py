"""调度 API."""

from fastapi import APIRouter

from app.services.schedule_service import schedule_service

router = APIRouter()


@router.post("/")
async def create_schedule(data: dict):
    s = schedule_service.create_schedule(
        org_id=data.get("org_id", ""),
        name=data.get("name", ""),
        prompt=data.get("prompt", ""),
        schedule_type=data.get("schedule_type", "cron"),
        cron_expression=data.get("cron_expression", ""),
        interval_minutes=data.get("interval_minutes", 0),
        run_at=data.get("run_at", ""),
        model=data.get("model", "auto"),
        mode=data.get("mode", "localhost"),
        playbook_id=data.get("playbook_id", ""),
        repo_url=data.get("repo_url", ""),
        max_runs=data.get("max_runs", 0),
        description=data.get("description", ""),
    )
    return {"id": s.id, "name": s.name}


@router.get("/")
async def list_schedules(org_id: str = ""):
    return {"schedules": schedule_service.list_schedules(org_id)}


@router.get("/{schedule_id}")
async def get_schedule(schedule_id: str):
    return schedule_service.get_schedule(schedule_id) or {"error": "not found"}


@router.post("/{schedule_id}/trigger")
async def trigger_run(schedule_id: str):
    run = schedule_service.trigger_run(schedule_id)
    if not run:
        return {"error": "not found"}
    return {"run_id": run.id, "session_id": run.session_id, "status": run.status}


@router.post("/{schedule_id}/pause")
async def pause_schedule(schedule_id: str):
    return {"ok": schedule_service.pause_schedule(schedule_id)}


@router.post("/{schedule_id}/resume")
async def resume_schedule(schedule_id: str):
    return {"ok": schedule_service.resume_schedule(schedule_id)}


@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: str):
    return {"ok": schedule_service.delete_schedule(schedule_id)}


@router.get("/{schedule_id}/runs")
async def get_runs(schedule_id: str):
    return {"runs": schedule_service.get_runs(schedule_id)}
