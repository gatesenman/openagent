"""审计日志 API / Audit log endpoints."""

from fastapi import APIRouter

from app.services.audit_service import audit_service

router = APIRouter()


@router.get("/")
async def query_audit_logs(
    user_id: str | None = None,
    session_id: str | None = None,
    action: str | None = None,
    resource_type: str | None = None,
    severity: str | None = None,
    limit: int = 50,
    offset: int = 0,
):
    """查询审计日志."""
    entries = audit_service.query(
        user_id=user_id,
        session_id=session_id,
        action=action,
        resource_type=resource_type,
        severity=severity,
        limit=limit,
        offset=offset,
    )
    return {"entries": entries, "total": audit_service.count()}


@router.get("/export")
async def export_audit_logs(format: str = "json"):
    """导出审计日志."""
    entries = audit_service.export(format=format)
    return {"entries": entries, "total": len(entries), "format": format}
