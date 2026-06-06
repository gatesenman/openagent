"""仓库管理 API / Repository management endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.repos_service import repos_service

router = APIRouter()


class AddRepoRequest(BaseModel):
    name: str
    url: str
    default_branch: str = "main"
    language: str = ""
    description: str = ""


@router.get("/")
async def list_repos(language: str | None = None):
    """列出已连接的仓库."""
    repos = repos_service.list_repos(language=language)
    return {"repos": repos, "total": len(repos)}


@router.post("/")
async def add_repo(req: AddRepoRequest):
    """添加仓库."""
    repo = repos_service.add_repo(
        name=req.name, url=req.url, default_branch=req.default_branch,
        language=req.language, description=req.description,
    )
    return repo.to_dict()


@router.get("/search")
async def search_repos(q: str = ""):
    """搜索仓库."""
    repos = repos_service.search_repos(q)
    return {"repos": repos, "total": len(repos)}


@router.get("/{repo_id}")
async def get_repo(repo_id: str):
    """获取仓库详情."""
    repo = repos_service.get_repo(repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="仓库不存在")
    return repo.to_dict()


@router.delete("/{repo_id}")
async def remove_repo(repo_id: str):
    """移除仓库."""
    if not repos_service.remove_repo(repo_id):
        raise HTTPException(status_code=404, detail="仓库不存在")
    return {"status": "removed", "id": repo_id}


@router.post("/{repo_id}/deepwiki/index")
async def trigger_deepwiki_index(repo_id: str):
    """触发 DeepWiki 索引."""
    try:
        result = await repos_service.trigger_deepwiki_index(repo_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{repo_id}/codemap/analyze")
async def trigger_codemap_analysis(repo_id: str):
    """触发 CodeMap 分析."""
    try:
        result = await repos_service.trigger_codemap_analysis(repo_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
