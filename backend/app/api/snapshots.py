"""快照 API."""

from fastapi import APIRouter

from app.services.snapshot_service import snapshot_service

router = APIRouter()


@router.post("/build")
async def build_snapshot(data: dict):
    snap = snapshot_service.build_snapshot(
        org_id=data.get("org_id", ""),
        blueprint_id=data.get("blueprint_id", ""),
        repo_id=data.get("repo_id", ""),
        name=data.get("name", ""),
        platform=data.get("platform", "ubuntu-22.04"),
    )
    return {"id": snap.id, "status": snap.status.value}


@router.get("/")
async def list_snapshots(org_id: str = "", blueprint_id: str = ""):
    return {"snapshots": snapshot_service.list_snapshots(org_id, blueprint_id)}


@router.get("/{snapshot_id}")
async def get_snapshot(snapshot_id: str):
    return snapshot_service.get_snapshot(snapshot_id) or {"error": "not found"}


@router.delete("/{snapshot_id}")
async def delete_snapshot(snapshot_id: str):
    return {"ok": snapshot_service.delete_snapshot(snapshot_id)}


@router.post("/{snapshot_id}/restore")
async def restore_snapshot(snapshot_id: str, data: dict):
    result = snapshot_service.restore_snapshot(snapshot_id, data.get("session_id", ""))
    return result or {"error": "snapshot not ready or not found"}
