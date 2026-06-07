"""CI/CD API."""

from fastapi import APIRouter

from app.services.cicd_service import cicd_service

router = APIRouter()


@router.post("/pipelines")
async def create_pipeline(data: dict):
    pipeline = cicd_service.create_pipeline(
        session_id=data.get("session_id", ""),
        provider=data.get("provider", "github_actions"),
        repo_url=data.get("repo_url", ""),
        branch=data.get("branch", "main"),
        commit_sha=data.get("commit_sha", ""),
        template=data.get("template", ""),
    )
    return {"id": pipeline.id}


@router.post("/pipelines/{pipeline_id}/run")
async def run_pipeline(pipeline_id: str):
    result = cicd_service.run_pipeline(pipeline_id)
    if not result:
        return {"error": "not found"}
    return {"status": result.status.value}


@router.get("/pipelines/{pipeline_id}")
async def get_pipeline(pipeline_id: str):
    return cicd_service.get_pipeline(pipeline_id) or {"error": "not found"}


@router.get("/pipelines")
async def list_pipelines(session_id: str = ""):
    return {"pipelines": cicd_service.list_pipelines(session_id)}


@router.get("/templates")
async def get_templates():
    return {"templates": cicd_service.get_templates()}
