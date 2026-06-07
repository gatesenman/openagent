"""环境快照服务 — 管理 Devbox 快照的构建、列表和恢复."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class SnapshotStatus(Enum):
    pending = "pending"
    building = "building"
    ready = "ready"
    failed = "failed"
    expired = "expired"


@dataclass
class Snapshot:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    org_id: str = ""
    blueprint_id: str = ""
    repo_id: str = ""
    name: str = ""
    status: SnapshotStatus = SnapshotStatus.pending
    image_path: str = ""
    size_bytes: int = 0
    platform: str = "ubuntu-22.04"
    build_log: list = field(default_factory=list)
    built_at: Optional[str] = None
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class SnapshotService:
    def __init__(self):
        self._snapshots: dict[str, Snapshot] = {}

    def build_snapshot(
        self,
        org_id: str,
        blueprint_id: str,
        repo_id: str = "",
        name: str = "",
        platform: str = "ubuntu-22.04",
    ) -> Snapshot:
        snap = Snapshot(
            org_id=org_id,
            blueprint_id=blueprint_id,
            repo_id=repo_id,
            name=name or f"snapshot-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
            platform=platform,
            status=SnapshotStatus.building,
        )
        # Phase 1: 模拟构建流程
        snap.build_log.append({"step": "clone_repo", "status": "success"})
        snap.build_log.append({"step": "run_initialize", "status": "success"})
        snap.build_log.append({"step": "run_maintenance", "status": "success"})
        snap.build_log.append({"step": "create_image", "status": "success"})
        snap.status = SnapshotStatus.ready
        snap.size_bytes = 2 * 1024 * 1024 * 1024  # 2GB
        snap.image_path = f"/snapshots/{snap.id}.qcow2"
        snap.built_at = datetime.now(timezone.utc).isoformat()
        self._snapshots[snap.id] = snap
        return snap

    def get_snapshot(self, snapshot_id: str) -> Optional[dict]:
        snap = self._snapshots.get(snapshot_id)
        if not snap:
            return None
        return {
            "id": snap.id,
            "org_id": snap.org_id,
            "blueprint_id": snap.blueprint_id,
            "name": snap.name,
            "status": snap.status.value,
            "platform": snap.platform,
            "size_bytes": snap.size_bytes,
            "image_path": snap.image_path,
            "build_log": snap.build_log,
            "built_at": snap.built_at,
            "created_at": snap.created_at,
        }

    def list_snapshots(self, org_id: str = "", blueprint_id: str = "") -> list[dict]:
        results = []
        for snap in self._snapshots.values():
            if org_id and snap.org_id != org_id:
                continue
            if blueprint_id and snap.blueprint_id != blueprint_id:
                continue
            results.append({
                "id": snap.id,
                "name": snap.name,
                "status": snap.status.value,
                "platform": snap.platform,
                "size_bytes": snap.size_bytes,
                "built_at": snap.built_at,
                "created_at": snap.created_at,
            })
        return sorted(results, key=lambda x: x["created_at"], reverse=True)

    def delete_snapshot(self, snapshot_id: str) -> bool:
        if snapshot_id in self._snapshots:
            del self._snapshots[snapshot_id]
            return True
        return False

    def restore_snapshot(self, snapshot_id: str, session_id: str) -> Optional[dict]:
        snap = self._snapshots.get(snapshot_id)
        if not snap or snap.status != SnapshotStatus.ready:
            return None
        return {
            "snapshot_id": snap.id,
            "session_id": session_id,
            "status": "restored",
            "image_path": snap.image_path,
        }


snapshot_service = SnapshotService()
