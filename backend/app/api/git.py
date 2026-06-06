"""Git API / Git integration endpoints.

通过沙箱执行 Git 操作。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.git_service import git_service
from app.sandbox.manager import sandbox_manager

router = APIRouter()


class CloneRequest(BaseModel):
    session_id: str
    repo_url: str
    target_dir: str = "workspace"
    branch: str | None = None
    depth: int | None = None


class CommitRequest(BaseModel):
    session_id: str
    message: str
    repo_dir: str = "workspace"


class PushRequest(BaseModel):
    session_id: str
    repo_dir: str = "workspace"
    remote: str = "origin"
    branch: str | None = None


class BranchRequest(BaseModel):
    session_id: str
    name: str
    repo_dir: str = "workspace"


class PRRequest(BaseModel):
    session_id: str
    title: str
    body: str = ""
    base: str = "main"
    repo_dir: str = "workspace"


def _get_sandbox(session_id: str):
    """获取会话沙箱."""
    sb = sandbox_manager.get_sandbox(session_id)
    if not sb:
        raise HTTPException(status_code=404, detail=f"会话 {session_id} 无关联沙箱")
    return sb


@router.post("/clone")
async def git_clone(req: CloneRequest):
    """在沙箱中克隆仓库."""
    sb = _get_sandbox(req.session_id)
    return await git_service.clone(
        sb, req.repo_url, req.target_dir, req.branch, req.depth
    )


@router.get("/status/{session_id}")
async def git_status(session_id: str, repo_dir: str = "workspace"):
    """获取 Git 状态."""
    sb = _get_sandbox(session_id)
    status = await git_service.status(sb, repo_dir)
    return {
        "branch": status.branch,
        "clean": status.clean,
        "staged": status.staged,
        "modified": status.modified,
        "untracked": status.untracked,
        "ahead": status.ahead,
        "behind": status.behind,
    }


@router.get("/diff/{session_id}")
async def git_diff(session_id: str, repo_dir: str = "workspace", staged: bool = False):
    """获取 Git diff."""
    sb = _get_sandbox(session_id)
    entries = await git_service.diff(sb, repo_dir, staged)
    return [
        {
            "path": e.path,
            "status": e.status,
            "additions": e.additions,
            "deletions": e.deletions,
        }
        for e in entries
    ]


@router.post("/commit")
async def git_commit(req: CommitRequest):
    """创建 Git commit."""
    sb = _get_sandbox(req.session_id)
    return await git_service.commit(sb, req.message, req.repo_dir)


@router.post("/push")
async def git_push(req: PushRequest):
    """推送到远程."""
    sb = _get_sandbox(req.session_id)
    return await git_service.push(sb, req.repo_dir, req.remote, req.branch)


@router.get("/log/{session_id}")
async def git_log(session_id: str, repo_dir: str = "workspace", limit: int = 20):
    """获取 Git log."""
    sb = _get_sandbox(session_id)
    entries = await git_service.log(sb, repo_dir, limit)
    return [
        {
            "sha": e.sha,
            "short_sha": e.short_sha,
            "message": e.message,
            "author": e.author,
            "date": e.date,
        }
        for e in entries
    ]


@router.post("/branch")
async def git_branch(req: BranchRequest):
    """创建并切换分支."""
    sb = _get_sandbox(req.session_id)
    return await git_service.branch(sb, req.name, req.repo_dir)


@router.post("/pr")
async def git_pr(req: PRRequest):
    """创建 Pull Request."""
    sb = _get_sandbox(req.session_id)
    return await git_service.create_pr(
        sb, req.title, req.body, req.base, repo_dir=req.repo_dir
    )
