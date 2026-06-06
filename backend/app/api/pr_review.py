"""PR Review API."""

from fastapi import APIRouter, HTTPException

from app.services.pr_review_service import pr_review_service

router = APIRouter()


@router.post("/review")
async def review_pr(data: dict):
    """审查 PR diff."""
    pr_id = data.get("pr_id", "")
    repo = data.get("repo", "")
    diff_text = data.get("diff", "")
    if not diff_text:
        raise HTTPException(status_code=400, detail="diff 内容不能为空")

    result = pr_review_service.review_diff(pr_id, repo, diff_text)
    return {
        "pr_id": result.pr_id,
        "risk_level": result.risk_level.value,
        "summary": result.summary,
        "files_reviewed": result.files_reviewed,
        "issues_found": result.issues_found,
        "comments": [
            {
                "id": c.id,
                "file": c.file_path,
                "line": c.line,
                "severity": c.severity.value,
                "message": c.message,
                "rule": c.rule,
            }
            for c in result.comments
        ],
    }


@router.get("/{pr_id}")
async def get_review_result(pr_id: str):
    """获取 PR 审查结果."""
    result = pr_review_service.get_result(pr_id)
    if not result:
        raise HTTPException(status_code=404, detail="审查结果不存在")
    return {
        "pr_id": result.pr_id,
        "risk_level": result.risk_level.value,
        "summary": result.summary,
        "issues_found": result.issues_found,
    }


@router.get("/rules/list")
async def list_rules():
    """获取审查规则."""
    return {"rules": pr_review_service.list_rules()}
