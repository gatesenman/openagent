"""蓝图管理服务 / Blueprint management service.

环境蓝图 (YAML 配置) 定义了 Devbox 的初始化和维护流程。
参考 Devin 的 initialize / maintenance / knowledge 三段式蓝图。
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum

import yaml

logger = logging.getLogger(__name__)


class SnapshotStatus(str, Enum):
    BUILDING = "building"
    READY = "ready"
    FAILED = "failed"


@dataclass
class Blueprint:
    """环境蓝图."""
    id: str
    name: str
    repo_id: str | None = None  # None = org level
    target: str = "repo"  # repo / org
    initialize: str = ""  # 初始化命令
    maintenance: str = ""  # 维护命令
    knowledge: list[dict] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "repo_id": self.repo_id,
            "target": self.target,
            "initialize": self.initialize,
            "maintenance": self.maintenance,
            "knowledge": self.knowledge,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    def to_yaml(self) -> str:
        data = {}
        if self.initialize:
            data["initialize"] = self.initialize
        if self.maintenance:
            data["maintenance"] = self.maintenance
        if self.knowledge:
            data["knowledge"] = self.knowledge
        return yaml.dump(data, allow_unicode=True, default_flow_style=False)


@dataclass
class Snapshot:
    """环境快照."""
    id: str
    blueprint_id: str
    status: SnapshotStatus = SnapshotStatus.BUILDING
    created_at: float = field(default_factory=time.time)
    size_mb: float = 0.0
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "blueprint_id": self.blueprint_id,
            "status": self.status.value,
            "created_at": self.created_at,
            "size_mb": self.size_mb,
            "error": self.error,
        }


class BlueprintService:
    """蓝图管理服务."""

    def __init__(self):
        self._blueprints: dict[str, Blueprint] = {}
        self._snapshots: dict[str, Snapshot] = {}
        self._init_defaults()

    def _init_defaults(self):
        """创建默认蓝图模板."""
        templates = [
            {
                "name": "Python + FastAPI",
                "initialize": "pip install uv\nuv venv .venv\nsource .venv/bin/activate",
                "maintenance": "uv sync\npip install -e .",
                "knowledge": [
                    {"name": "test", "contents": "pytest tests/ -v"},
                    {"name": "lint", "contents": "ruff check ."},
                ],
            },
            {
                "name": "Node.js + Next.js",
                "initialize": "corepack enable\npnpm install",
                "maintenance": "pnpm install",
                "knowledge": [
                    {"name": "test", "contents": "pnpm test"},
                    {"name": "lint", "contents": "pnpm lint"},
                    {"name": "startup", "contents": "pnpm dev"},
                ],
            },
            {
                "name": "Rust + Cargo",
                "initialize": "rustup update stable",
                "maintenance": "cargo fetch",
                "knowledge": [
                    {"name": "test", "contents": "cargo test"},
                    {"name": "lint", "contents": "cargo clippy"},
                ],
            },
        ]
        for tmpl in templates:
            bp = Blueprint(
                id=str(uuid.uuid4()),
                name=tmpl["name"],
                target="template",
                initialize=tmpl["initialize"],
                maintenance=tmpl["maintenance"],
                knowledge=tmpl["knowledge"],
            )
            self._blueprints[bp.id] = bp

    def get_blueprint(self, blueprint_id: str) -> Blueprint | None:
        return self._blueprints.get(blueprint_id)

    def list_blueprints(
        self, target: str | None = None, repo_id: str | None = None,
    ) -> list[dict]:
        results = []
        for bp in self._blueprints.values():
            if target and bp.target != target:
                continue
            if repo_id and bp.repo_id != repo_id:
                continue
            results.append(bp.to_dict())
        return results

    def create_blueprint(
        self,
        name: str,
        target: str = "repo",
        repo_id: str | None = None,
        initialize: str = "",
        maintenance: str = "",
        knowledge: list[dict] | None = None,
    ) -> Blueprint:
        bp = Blueprint(
            id=str(uuid.uuid4()),
            name=name,
            repo_id=repo_id,
            target=target,
            initialize=initialize,
            maintenance=maintenance,
            knowledge=knowledge or [],
        )
        self._blueprints[bp.id] = bp
        logger.info("蓝图已创建: %s [target=%s]", name, target)
        return bp

    def update_blueprint(
        self, blueprint_id: str, **kwargs,
    ) -> Blueprint | None:
        bp = self._blueprints.get(blueprint_id)
        if not bp:
            return None
        for key, value in kwargs.items():
            if hasattr(bp, key) and value is not None:
                setattr(bp, key, value)
        bp.updated_at = time.time()
        return bp

    def delete_blueprint(self, blueprint_id: str) -> bool:
        if blueprint_id in self._blueprints:
            del self._blueprints[blueprint_id]
            return True
        return False

    async def build_snapshot(self, blueprint_id: str) -> Snapshot:
        """构建快照（异步模拟）."""
        bp = self._blueprints.get(blueprint_id)
        if not bp:
            raise ValueError("蓝图不存在")

        snapshot = Snapshot(
            id=str(uuid.uuid4()),
            blueprint_id=blueprint_id,
        )
        self._snapshots[snapshot.id] = snapshot

        # Phase 1: 模拟构建
        snapshot.status = SnapshotStatus.READY
        snapshot.size_mb = 256.0
        logger.info("快照已构建: %s (blueprint=%s)", snapshot.id, bp.name)
        return snapshot

    def list_snapshots(self, blueprint_id: str | None = None) -> list[dict]:
        results = []
        for s in self._snapshots.values():
            if blueprint_id and s.blueprint_id != blueprint_id:
                continue
            results.append(s.to_dict())
        return results


blueprint_service = BlueprintService()
