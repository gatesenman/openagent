"""安全 API / Security endpoints.

OWASP LLM Top 10 安全扫描、危险命令检测、敏感文件保护。
"""

from pydantic import BaseModel
from fastapi import APIRouter

from app.services.security_service import security_service

router = APIRouter()


class ScanRequest(BaseModel):
    text: str


class CommandCheckRequest(BaseModel):
    command: str


class FileCheckRequest(BaseModel):
    filepath: str


@router.post("/scan")
async def security_scan(req: ScanRequest):
    """执行 OWASP LLM Top 10 全面安全扫描."""
    report = security_service.run_full_scan(req.text)
    return {
        "timestamp": report.timestamp,
        "total_checks": report.total_checks,
        "passed": report.passed,
        "failed": report.failed,
        "risk_score": report.risk_score,
        "checks": report.checks,
    }


@router.post("/check-command")
async def check_dangerous_command(req: CommandCheckRequest):
    """检查命令是否危险."""
    check = security_service.check_dangerous_command(req.command)
    return {
        "command": req.command,
        "safe": check.passed,
        "risk_level": check.risk_level.value,
        "details": check.details,
    }


@router.post("/check-file")
async def check_sensitive_file(req: FileCheckRequest):
    """检查文件是否为敏感文件."""
    check = security_service.check_sensitive_file(req.filepath)
    return {
        "filepath": req.filepath,
        "safe": check.passed,
        "risk_level": check.risk_level.value,
        "details": check.details,
    }


@router.get("/owasp-rules")
async def get_owasp_rules():
    """获取 OWASP LLM Top 10 规则列表."""
    return {"rules": security_service.get_owasp_rules()}


@router.get("/report")
async def get_security_overview():
    """获取安全概览."""
    return {
        "owasp_version": "LLM Top 10 v2025",
        "rules_count": len(security_service.get_owasp_rules()),
        "dangerous_command_patterns": 14,
        "sensitive_file_patterns": 16,
        "features": [
            "Prompt Injection Detection",
            "Insecure Output Handling",
            "Sensitive Information Disclosure Prevention",
            "System Prompt Leakage Prevention",
            "Dangerous Command Blocking",
            "Sensitive File Access Control",
        ],
    }
