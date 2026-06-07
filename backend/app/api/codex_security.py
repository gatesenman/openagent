"""Codex Security API — Enterprise-grade code security endpoints.

Inspired by Codex Security principles: SAST, SCA, secret detection,
license compliance, SBOM, IaC scanning, compliance reporting, and policy engine.
"""

from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter

from app.services.codex_security import codex_security, ComplianceFramework

router = APIRouter()


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------

class CodeScanRequest(BaseModel):
    source_code: str = Field(..., description="Source code to scan")
    filename: str = Field("", description="File path for context")
    language: str = Field("python", description="Programming language")


class FullScanRequest(BaseModel):
    source_code: str
    filename: str = ""
    language: str = "python"
    dependencies: Optional[list[dict]] = None
    packages_with_licenses: Optional[list[dict]] = None
    iac_content: Optional[str] = None
    iac_filename: Optional[str] = None


class SecretScanRequest(BaseModel):
    content: str
    filename: str = ""


class DependencyScanRequest(BaseModel):
    dependencies: list[dict] = Field(
        ..., description="List of {name, version, ecosystem} dicts"
    )


class LicenseCheckRequest(BaseModel):
    packages: list[dict] = Field(
        ..., description="List of {name, version, license} dicts"
    )
    allowed_categories: Optional[list[str]] = None


class SBOMRequest(BaseModel):
    packages: list[dict]
    project_name: str = "openagent"


class IaCScanRequest(BaseModel):
    content: str
    filename: str = ""


class ComplianceRequest(BaseModel):
    framework: str = Field(..., description="soc2, iso27001, gdpr, hipaa, pci_dss, nist_800_53, cis_benchmark")
    enabled_features: Optional[dict] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/capabilities")
async def get_capabilities():
    """Return Codex Security engine capabilities and statistics."""
    return codex_security.get_capabilities()


@router.post("/scan/sast")
async def run_sast_scan(req: CodeScanRequest):
    """Run Static Application Security Testing (SAST) on source code."""
    findings = codex_security.run_sast(req.source_code, req.filename, req.language)
    return {
        "scan_type": "sast",
        "total_findings": len(findings),
        "findings": [{
            "id": f.id, "title": f.title, "severity": f.severity.value,
            "cwe_id": f.cwe_id, "file_path": f.file_path,
            "line_number": f.line_number, "description": f.description,
            "remediation": f.remediation, "priority": f.remediation_priority.value,
        } for f in findings],
    }


@router.post("/scan/secrets")
async def run_secret_scan(req: SecretScanRequest):
    """Detect hardcoded secrets in source code."""
    findings = codex_security.scan_secrets(req.content, req.filename)
    return {
        "scan_type": "secret",
        "total_findings": len(findings),
        "findings": [{
            "type": s.secret_type, "file_path": s.file_path,
            "line_number": s.line_number, "severity": s.severity.value,
            "redacted_value": s.redacted_value, "entropy": s.entropy,
        } for s in findings],
    }


@router.post("/scan/dependencies")
async def run_dependency_scan(req: DependencyScanRequest):
    """Scan dependencies for known CVE vulnerabilities."""
    findings = codex_security.scan_dependencies(req.dependencies)
    return {
        "scan_type": "sca",
        "total_findings": len(findings),
        "findings": [{
            "package": d.package_name, "installed": d.installed_version,
            "fixed": d.fixed_version, "severity": d.severity.value,
            "cve_id": d.cve_id, "cvss_score": d.cvss_score,
            "description": d.description,
        } for d in findings],
    }


@router.post("/scan/licenses")
async def run_license_check(req: LicenseCheckRequest):
    """Check license compliance for project dependencies."""
    results = codex_security.check_licenses(req.packages, req.allowed_categories)
    compliant = [r for r in results if r.compliant]
    non_compliant = [r for r in results if not r.compliant]
    return {
        "scan_type": "license",
        "total_packages": len(results),
        "compliant_count": len(compliant),
        "non_compliant_count": len(non_compliant),
        "results": [{
            "package": l.package_name, "version": l.version,
            "license": l.license_id, "license_name": l.license_name,
            "category": l.category, "compliant": l.compliant,
            "risk_level": l.risk_level,
        } for l in results],
    }


@router.post("/scan/iac")
async def run_iac_scan(req: IaCScanRequest):
    """Scan Infrastructure as Code files (Docker, K8s, Terraform)."""
    findings = codex_security.scan_iac(req.content, req.filename)
    return {
        "scan_type": "iac",
        "total_findings": len(findings),
        "findings": [{
            "id": f.id, "title": f.title, "severity": f.severity.value,
            "file_path": f.file_path, "remediation": f.remediation,
        } for f in findings],
    }


@router.post("/scan/full")
async def run_full_scan(req: FullScanRequest):
    """Run comprehensive security scan combining all engines."""
    return codex_security.run_full_scan(
        source_code=req.source_code,
        filename=req.filename,
        language=req.language,
        dependencies=req.dependencies,
        packages_with_licenses=req.packages_with_licenses,
        iac_content=req.iac_content,
        iac_filename=req.iac_filename,
    )


@router.post("/sbom")
async def generate_sbom(req: SBOMRequest):
    """Generate Software Bill of Materials (CycloneDX format)."""
    return codex_security.generate_sbom(req.packages, req.project_name)


@router.post("/compliance")
async def run_compliance_check(req: ComplianceRequest):
    """Run compliance check against a framework (SOC2, ISO27001, GDPR, HIPAA)."""
    try:
        framework = ComplianceFramework(req.framework)
    except ValueError:
        return {"error": f"Unknown framework: {req.framework}",
                "supported": [f.value for f in ComplianceFramework]}
    results = codex_security.run_compliance_check(framework, req.enabled_features)
    passed = sum(1 for r in results if r.status == "passed")
    return {
        "framework": req.framework,
        "total_controls": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "pass_rate": round(passed / len(results) * 100, 1) if results else 100.0,
        "controls": [{
            "control_id": c.control_id, "control_name": c.control_name,
            "status": c.status, "evidence": c.evidence,
            "remediation": c.remediation,
        } for c in results],
    }


@router.get("/policies")
async def get_policies():
    """List active security policies."""
    return {
        "total": len(codex_security.policies),
        "policies": [{
            "id": p.id, "name": p.name, "description": p.description,
            "action": p.action.value, "enabled": p.enabled,
            "conditions": p.conditions,
        } for p in codex_security.policies],
    }


@router.get("/scan-history")
async def get_scan_history():
    """Return scan history for trend analysis."""
    return {"history": codex_security.get_scan_history()}
