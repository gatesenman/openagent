"""蓝图管理 API / Blueprint management endpoints.

环境配置（初始化/维护/知识）和快照管理。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.blueprint_service import blueprint_service

router = APIRouter()


class CreateBlueprintRequest(BaseModel):
    name: str
    target: str = "repo"
    repo_id: str | None = None
    initialize: str = ""
    maintenance: str = ""
    knowledge: list[dict] | None = None


class UpdateBlueprintRequest(BaseModel):
    name: str | None = None
    initialize: str | None = None
    maintenance: str | None = None
    knowledge: list[dict] | None = None


@router.get("/")
async def list_blueprints(target: str | None = None, repo_id: str | None = None):
    """列出蓝图."""
    blueprints = blueprint_service.list_blueprints(target=target, repo_id=repo_id)
    return {"blueprints": blueprints, "total": len(blueprints)}


@router.post("/")
async def create_blueprint(req: CreateBlueprintRequest):
    """创建蓝图."""
    bp = blueprint_service.create_blueprint(
        name=req.name,
        target=req.target,
        repo_id=req.repo_id,
        initialize=req.initialize,
        maintenance=req.maintenance,
        knowledge=req.knowledge,
    )
    return bp.to_dict()


@router.get("/{blueprint_id}")
async def get_blueprint(blueprint_id: str):
    """获取蓝图详情."""
    bp = blueprint_service.get_blueprint(blueprint_id)
    if not bp:
        raise HTTPException(status_code=404, detail="蓝图不存在")
    return bp.to_dict()


@router.put("/{blueprint_id}")
async def update_blueprint(blueprint_id: str, req: UpdateBlueprintRequest):
    """更新蓝图."""
    bp = blueprint_service.update_blueprint(
        blueprint_id,
        name=req.name,
        initialize=req.initialize,
        maintenance=req.maintenance,
        knowledge=req.knowledge,
    )
    if not bp:
        raise HTTPException(status_code=404, detail="蓝图不存在")
    return bp.to_dict()


@router.delete("/{blueprint_id}")
async def delete_blueprint(blueprint_id: str):
    """删除蓝图."""
    if not blueprint_service.delete_blueprint(blueprint_id):
        raise HTTPException(status_code=404, detail="蓝图不存在")
    return {"status": "deleted", "id": blueprint_id}


@router.post("/build")
async def build_snapshot(blueprint_id: str):
    """构建快照."""
    try:
        snapshot = await blueprint_service.build_snapshot(blueprint_id)
        return snapshot.to_dict()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/snapshots/list")
async def list_snapshots(blueprint_id: str | None = None):
    """列出快照."""
    snapshots = blueprint_service.list_snapshots(blueprint_id=blueprint_id)
    return {"snapshots": snapshots, "total": len(snapshots)}


@router.get("/{blueprint_id}/yaml")
async def get_blueprint_yaml(blueprint_id: str):
    """以 YAML 格式返回蓝图配置."""
    bp = blueprint_service.get_blueprint(blueprint_id)
    if not bp:
        raise HTTPException(status_code=404, detail="蓝图不存在")
    return {"yaml": bp.to_yaml(), "name": bp.name}
