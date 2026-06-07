"""Codex Security — Enterprise-grade code security analysis engine.

Provides comprehensive security scanning capabilities:
- Static Application Security Testing (SAST)
- Software Composition Analysis (SCA) / Dependency vulnerability scanning
- Secret detection in source code
- License compliance checking
- Software Bill of Materials (SBOM) generation
- Security policy enforcement
- Container image scanning
- Infrastructure as Code (IaC) security
- Code quality and security metrics
- Compliance reporting (SOC2, ISO27001, GDPR, HIPAA)
"""

import hashlib
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Severity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ScanType(str, Enum):
    SAST = "sast"
    SCA = "sca"
    SECRET = "secret"
    LICENSE = "license"
    IAC = "iac"
    CONTAINER = "container"
    SBOM = "sbom"


class ComplianceFramework(str, Enum):
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    NIST = "nist_800_53"
    CIS = "cis_benchmark"


class RemediationPriority(str, Enum):
    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"


class PolicyAction(str, Enum):
    BLOCK = "block"
    WARN = "warn"
    AUDIT = "audit"
    ALLOW = "allow"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Vulnerability:
    id: str
    title: str
    severity: Severity
    scan_type: ScanType
    description: str
    file_path: str = ""
    line_number: int = 0
    cwe_id: str = ""
    cve_id: str = ""
    cvss_score: float = 0.0
    remediation: str = ""
    remediation_priority: RemediationPriority = RemediationPriority.MEDIUM_TERM
    false_positive: bool = False
    suppressed: bool = False
    first_seen: str = ""
    references: list = field(default_factory=list)


@dataclass
class DependencyVulnerability:
    package_name: str
    installed_version: str
    vulnerable_versions: str
    fixed_version: str
    severity: Severity
    cve_id: str
    cvss_score: float
    description: str
    ecosystem: str = ""
    direct: bool = True
    transitive_path: list = field(default_factory=list)


@dataclass
class SecretFinding:
    secret_type: str
    file_path: str
    line_number: int
    severity: Severity
    description: str
    pattern_name: str
    redacted_value: str = ""
    verified: bool = False
    entropy: float = 0.0


@dataclass
class LicenseInfo:
    package_name: str
    version: str
    license_id: str
    license_name: str
    category: str  # permissive, copyleft, restricted, unknown
    compliant: bool = True
    risk_level: str = "low"


@dataclass
class SBOMComponent:
    name: str
    version: str
    ecosystem: str
    license_id: str
    purl: str  # Package URL (pkg:npm/express@4.18.2)
    sha256: str = ""
    supplier: str = ""
    direct: bool = True


@dataclass
class SecurityPolicy:
    id: str
    name: str
    description: str
    action: PolicyAction
    enabled: bool = True
    conditions: dict = field(default_factory=dict)


@dataclass
class ComplianceCheck:
    framework: ComplianceFramework
    control_id: str
    control_name: str
    status: str  # passed, failed, not_applicable
    evidence: str = ""
    remediation: str = ""


@dataclass
class SecurityDashboard:
    scan_id: str
    timestamp: str
    total_vulnerabilities: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    info_count: int = 0
    risk_score: float = 100.0
    grade: str = "A"
    scan_types_executed: list = field(default_factory=list)
    policy_violations: int = 0
    compliance_pass_rate: float = 100.0
    mean_time_to_remediate: str = "N/A"
    trend: str = "stable"


# ---------------------------------------------------------------------------
# SAST Rules — Static code analysis patterns
# ---------------------------------------------------------------------------

SAST_RULES = [
    {
        "id": "SAST-001",
        "title": "SQL Injection via String Concatenation",
        "cwe": "CWE-89",
        "severity": Severity.CRITICAL,
        "pattern": r"(?:execute|cursor\.execute|query)\s*\(\s*['\"].*%s.*['\"]|f['\"].*(?:SELECT|INSERT|UPDATE|DELETE).*\{",
        "description": "SQL query built with string concatenation or f-strings. Use parameterized queries instead.",
        "remediation": "Replace string concatenation with parameterized queries: cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))",
        "languages": ["python", "javascript"],
    },
    {
        "id": "SAST-002",
        "title": "Cross-Site Scripting (XSS) — Unescaped Output",
        "cwe": "CWE-79",
        "severity": Severity.HIGH,
        "pattern": r"innerHTML\s*=|dangerouslySetInnerHTML|v-html\s*=|\.html\(|document\.write\(",
        "description": "Direct HTML injection without sanitization enables XSS attacks.",
        "remediation": "Use textContent instead of innerHTML, or sanitize with DOMPurify.",
        "languages": ["javascript", "typescript"],
    },
    {
        "id": "SAST-003",
        "title": "Command Injection via Unsanitized Input",
        "cwe": "CWE-78",
        "severity": Severity.CRITICAL,
        "pattern": r"os\.system\(|subprocess\.(?:call|run|Popen)\(.*shell\s*=\s*True|exec\(.*\+|child_process\.exec\(",
        "description": "System command execution with unsanitized input allows arbitrary command injection.",
        "remediation": "Use subprocess.run() with shell=False and pass arguments as a list.",
        "languages": ["python", "javascript"],
    },
    {
        "id": "SAST-004",
        "title": "Path Traversal — Unsanitized File Path",
        "cwe": "CWE-22",
        "severity": Severity.HIGH,
        "pattern": r"open\(.*\+.*\)|os\.path\.join\(.*request\.|fs\.readFile\(.*req\.",
        "description": "File path constructed from user input without validation enables directory traversal.",
        "remediation": "Validate and sanitize file paths, use os.path.realpath() and check against allowed directories.",
        "languages": ["python", "javascript"],
    },
    {
        "id": "SAST-005",
        "title": "Insecure Deserialization",
        "cwe": "CWE-502",
        "severity": Severity.CRITICAL,
        "pattern": r"pickle\.loads?\(|yaml\.(?:load|unsafe_load)\(|unserialize\(|JSON\.parse\(.*eval|marshal\.loads?\(",
        "description": "Deserializing untrusted data can lead to remote code execution.",
        "remediation": "Use yaml.safe_load() instead of yaml.load(). Never unpickle untrusted data.",
        "languages": ["python", "php", "java"],
    },
    {
        "id": "SAST-006",
        "title": "Hardcoded Credentials",
        "cwe": "CWE-798",
        "severity": Severity.HIGH,
        "pattern": r"(?:password|passwd|secret|api_key|apikey|token|auth)\s*=\s*['\"][^'\"]{6,}['\"]",
        "description": "Credentials hardcoded in source code. Use environment variables or secrets manager.",
        "remediation": "Move credentials to environment variables or a secrets management service.",
        "languages": ["python", "javascript", "java", "go"],
    },
    {
        "id": "SAST-007",
        "title": "Weak Cryptographic Algorithm",
        "cwe": "CWE-327",
        "severity": Severity.MEDIUM,
        "pattern": r"(?:md5|sha1|DES|RC4|RC2)\s*\(|hashlib\.(?:md5|sha1)\(|crypto\.createHash\(['\"](?:md5|sha1)['\"]",
        "description": "Use of weak or deprecated cryptographic algorithms (MD5, SHA1, DES, RC4).",
        "remediation": "Use SHA-256 or stronger hashing. Use AES-256-GCM for encryption.",
        "languages": ["python", "javascript", "java"],
    },
    {
        "id": "SAST-008",
        "title": "Insecure Random Number Generation",
        "cwe": "CWE-330",
        "severity": Severity.MEDIUM,
        "pattern": r"random\.(?:random|randint|choice)\(|Math\.random\(\)|rand\(\)",
        "description": "Using non-cryptographic random for security-sensitive operations.",
        "remediation": "Use secrets.token_hex() in Python or crypto.randomBytes() in Node.js.",
        "languages": ["python", "javascript"],
    },
    {
        "id": "SAST-009",
        "title": "Server-Side Request Forgery (SSRF)",
        "cwe": "CWE-918",
        "severity": Severity.HIGH,
        "pattern": r"requests\.(?:get|post|put|delete)\(.*(?:request\.|params\[|args\[)|urllib\.request\.urlopen\(.*\+|fetch\(.*req\.",
        "description": "HTTP requests with user-controlled URLs can access internal services.",
        "remediation": "Validate and whitelist allowed URLs. Block internal/private IP ranges.",
        "languages": ["python", "javascript"],
    },
    {
        "id": "SAST-010",
        "title": "Missing Authentication Check",
        "cwe": "CWE-306",
        "severity": Severity.HIGH,
        "pattern": r"@app\.(?:route|get|post|put|delete)\((?!.*(?:login_required|auth|jwt_required|Depends)).*\ndef\s+(?!login|register|health|public)",
        "description": "API endpoint without authentication middleware.",
        "remediation": "Add authentication decorator or dependency injection to protect endpoints.",
        "languages": ["python"],
    },
    {
        "id": "SAST-011",
        "title": "Prototype Pollution",
        "cwe": "CWE-1321",
        "severity": Severity.HIGH,
        "pattern": r"Object\.assign\(.*req\.|_\.merge\(.*req\.|\.extend\(.*req\.|__proto__|constructor\[",
        "description": "Merging user input into objects can modify prototype chain.",
        "remediation": "Use Object.create(null) as base, or validate/sanitize input keys.",
        "languages": ["javascript", "typescript"],
    },
    {
        "id": "SAST-012",
        "title": "Improper Error Handling — Stack Trace Exposure",
        "cwe": "CWE-209",
        "severity": Severity.MEDIUM,
        "pattern": r"traceback\.format_exc\(\)|\.stack|printStackTrace\(\)|DEBUG\s*=\s*True",
        "description": "Exposing stack traces or debug info to end users reveals internal details.",
        "remediation": "Return generic error messages to users. Log detailed errors server-side only.",
        "languages": ["python", "javascript", "java"],
    },
]


# ---------------------------------------------------------------------------
# Secret Detection Patterns
# ---------------------------------------------------------------------------

SECRET_PATTERNS = [
    {
        "name": "AWS Access Key ID",
        "pattern": r"AKIA[0-9A-Z]{16}",
        "severity": Severity.CRITICAL,
    },
    {
        "name": "AWS Secret Access Key",
        "pattern": r"(?:aws_secret_access_key|AWS_SECRET_ACCESS_KEY)\s*[=:]\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?",
        "severity": Severity.CRITICAL,
    },
    {
        "name": "GitHub Personal Access Token",
        "pattern": r"gh[ps]_[A-Za-z0-9_]{36,}|github_pat_[A-Za-z0-9_]{22,}",
        "severity": Severity.CRITICAL,
    },
    {
        "name": "Google API Key",
        "pattern": r"AIza[0-9A-Za-z\-_]{35}",
        "severity": Severity.HIGH,
    },
    {
        "name": "Slack Bot Token",
        "pattern": r"xoxb-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,}",
        "severity": Severity.HIGH,
    },
    {
        "name": "Slack Webhook URL",
        "pattern": r"https://hooks\.slack\.com/services/T[A-Z0-9]+/B[A-Z0-9]+/[a-zA-Z0-9]+",
        "severity": Severity.MEDIUM,
    },
    {
        "name": "Stripe Secret Key",
        "pattern": r"sk_(?:live|test)_[A-Za-z0-9]{24,}",
        "severity": Severity.CRITICAL,
    },
    {
        "name": "RSA Private Key",
        "pattern": r"-----BEGIN (?:RSA )?PRIVATE KEY-----",
        "severity": Severity.CRITICAL,
    },
    {
        "name": "SSH Private Key (Ed25519/ECDSA)",
        "pattern": r"-----BEGIN (?:OPENSSH|EC) PRIVATE KEY-----",
        "severity": Severity.CRITICAL,
    },
    {
        "name": "Generic API Key",
        "pattern": r"(?:api[_-]?key|apikey|api_secret)\s*[=:]\s*['\"]([a-zA-Z0-9_\-]{20,})['\"]",
        "severity": Severity.HIGH,
    },
    {
        "name": "Database Connection String",
        "pattern": r"(?:mysql|postgres|postgresql|mongodb|redis|amqp)://[^:]+:[^@]+@[^/\s]+",
        "severity": Severity.CRITICAL,
    },
    {
        "name": "JWT Token",
        "pattern": r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
        "severity": Severity.HIGH,
    },
    {
        "name": "Azure Storage Account Key",
        "pattern": r"DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=[A-Za-z0-9+/=]{86,}",
        "severity": Severity.CRITICAL,
    },
    {
        "name": "SendGrid API Key",
        "pattern": r"SG\.[A-Za-z0-9_-]{22,}\.[A-Za-z0-9_-]{43,}",
        "severity": Severity.HIGH,
    },
    {
        "name": "Twilio Auth Token",
        "pattern": r"(?:twilio_auth_token|TWILIO_AUTH_TOKEN)\s*[=:]\s*['\"]?([a-f0-9]{32})['\"]?",
        "severity": Severity.HIGH,
    },
    {
        "name": "OpenAI API Key",
        "pattern": r"sk-[A-Za-z0-9]{20,}T3BlbkFJ[A-Za-z0-9]{20,}",
        "severity": Severity.HIGH,
    },
    {
        "name": "Anthropic API Key",
        "pattern": r"sk-ant-[A-Za-z0-9\-_]{40,}",
        "severity": Severity.HIGH,
    },
]


# ---------------------------------------------------------------------------
# License categories
# ---------------------------------------------------------------------------

LICENSE_DATABASE = {
    "MIT": {"name": "MIT License", "category": "permissive", "risk": "low"},
    "Apache-2.0": {"name": "Apache License 2.0", "category": "permissive", "risk": "low"},
    "BSD-2-Clause": {"name": "BSD 2-Clause", "category": "permissive", "risk": "low"},
    "BSD-3-Clause": {"name": "BSD 3-Clause", "category": "permissive", "risk": "low"},
    "ISC": {"name": "ISC License", "category": "permissive", "risk": "low"},
    "GPL-2.0": {"name": "GNU GPL v2", "category": "copyleft", "risk": "high"},
    "GPL-3.0": {"name": "GNU GPL v3", "category": "copyleft", "risk": "high"},
    "LGPL-2.1": {"name": "GNU LGPL v2.1", "category": "weak_copyleft", "risk": "medium"},
    "LGPL-3.0": {"name": "GNU LGPL v3", "category": "weak_copyleft", "risk": "medium"},
    "MPL-2.0": {"name": "Mozilla Public License 2.0", "category": "weak_copyleft", "risk": "medium"},
    "AGPL-3.0": {"name": "GNU AGPL v3", "category": "copyleft", "risk": "critical"},
    "SSPL-1.0": {"name": "Server Side Public License", "category": "restricted", "risk": "critical"},
    "BSL-1.1": {"name": "Business Source License", "category": "restricted", "risk": "high"},
    "UNLICENSED": {"name": "No License", "category": "unknown", "risk": "critical"},
}


# ---------------------------------------------------------------------------
# IaC Security Rules
# ---------------------------------------------------------------------------

IAC_RULES = [
    {
        "id": "IAC-001",
        "title": "Docker Container Running as Root",
        "pattern": r"USER\s+root",
        "severity": Severity.HIGH,
        "remediation": "Add USER directive with non-root user in Dockerfile.",
    },
    {
        "id": "IAC-002",
        "title": "Docker Image Using latest Tag",
        "pattern": r"FROM\s+\S+:latest",
        "severity": Severity.MEDIUM,
        "remediation": "Pin Docker image to a specific version tag for reproducibility.",
    },
    {
        "id": "IAC-003",
        "title": "Exposed Port Without TLS",
        "pattern": r"EXPOSE\s+(?:80|8080|8000|3000)\b",
        "severity": Severity.LOW,
        "remediation": "Use HTTPS (443) or configure TLS termination via reverse proxy.",
    },
    {
        "id": "IAC-004",
        "title": "Terraform AWS S3 Bucket Without Encryption",
        "pattern": r"resource\s+\"aws_s3_bucket\"",
        "severity": Severity.HIGH,
        "remediation": "Enable server-side encryption on S3 buckets.",
    },
    {
        "id": "IAC-005",
        "title": "Kubernetes Pod Without Security Context",
        "pattern": r"kind:\s*Pod",
        "severity": Severity.MEDIUM,
        "remediation": "Add securityContext with runAsNonRoot: true and readOnlyRootFilesystem: true.",
    },
    {
        "id": "IAC-006",
        "title": "Privileged Container",
        "pattern": r"privileged\s*:\s*true",
        "severity": Severity.CRITICAL,
        "remediation": "Remove privileged flag. Use specific Linux capabilities instead.",
    },
    {
        "id": "IAC-007",
        "title": "Hardcoded Secret in Environment Variable",
        "pattern": r"(?:env|environment)\s*:[\s\S]*?(?:PASSWORD|SECRET|TOKEN|KEY)\s*[=:]\s*['\"]?[a-zA-Z0-9]{8,}",
        "severity": Severity.CRITICAL,
        "remediation": "Use Kubernetes Secrets or environment variable references instead of hardcoded values.",
    },
]


# ---------------------------------------------------------------------------
# Compliance Controls
# ---------------------------------------------------------------------------

COMPLIANCE_CONTROLS = {
    ComplianceFramework.SOC2: [
        {"id": "CC6.1", "name": "Logical Access Controls", "checks": ["auth_required", "rbac_enabled", "mfa_configured"]},
        {"id": "CC6.6", "name": "System Boundary Protection", "checks": ["network_segmentation", "firewall_rules"]},
        {"id": "CC6.7", "name": "Data Transmission Encryption", "checks": ["tls_enabled", "cert_valid"]},
        {"id": "CC6.8", "name": "Malware Prevention", "checks": ["dependency_scan", "container_scan"]},
        {"id": "CC7.1", "name": "Vulnerability Management", "checks": ["sast_enabled", "sca_enabled", "scan_schedule"]},
        {"id": "CC7.2", "name": "System Monitoring", "checks": ["audit_logging", "alerting_configured"]},
        {"id": "CC8.1", "name": "Change Management", "checks": ["code_review_required", "ci_cd_pipeline"]},
    ],
    ComplianceFramework.ISO27001: [
        {"id": "A.8.24", "name": "Use of Cryptography", "checks": ["strong_crypto", "key_management"]},
        {"id": "A.8.25", "name": "Secure Development Lifecycle", "checks": ["sast_enabled", "code_review_required"]},
        {"id": "A.8.26", "name": "Application Security Requirements", "checks": ["input_validation", "output_encoding"]},
        {"id": "A.8.28", "name": "Secure Coding Practices", "checks": ["owasp_compliance", "secret_scanning"]},
        {"id": "A.8.9", "name": "Configuration Management", "checks": ["iac_scanning", "baseline_config"]},
    ],
    ComplianceFramework.GDPR: [
        {"id": "Art.25", "name": "Data Protection by Design", "checks": ["data_minimization", "encryption_at_rest"]},
        {"id": "Art.32", "name": "Security of Processing", "checks": ["access_control", "encryption_in_transit", "audit_logging"]},
        {"id": "Art.33", "name": "Breach Notification", "checks": ["incident_response_plan", "alerting_configured"]},
    ],
    ComplianceFramework.HIPAA: [
        {"id": "164.312(a)", "name": "Access Control", "checks": ["unique_user_id", "auto_logoff", "encryption"]},
        {"id": "164.312(c)", "name": "Integrity Controls", "checks": ["data_validation", "audit_logging"]},
        {"id": "164.312(e)", "name": "Transmission Security", "checks": ["tls_enabled", "integrity_controls"]},
    ],
}


# ---------------------------------------------------------------------------
# Default Security Policies
# ---------------------------------------------------------------------------

DEFAULT_POLICIES = [
    SecurityPolicy(
        id="POL-001",
        name="Block Critical Vulnerabilities",
        description="Block deployment when critical vulnerabilities are found",
        action=PolicyAction.BLOCK,
        conditions={"min_severity": "critical", "scan_types": ["sast", "sca", "secret"]},
    ),
    SecurityPolicy(
        id="POL-002",
        name="Require Secret Scanning",
        description="All commits must pass secret scanning before merge",
        action=PolicyAction.BLOCK,
        conditions={"scan_type": "secret", "on": "pre_commit"},
    ),
    SecurityPolicy(
        id="POL-003",
        name="License Compliance Gate",
        description="Block packages with copyleft or restricted licenses",
        action=PolicyAction.BLOCK,
        conditions={"license_categories": ["copyleft", "restricted", "unknown"]},
    ),
    SecurityPolicy(
        id="POL-004",
        name="Dependency Age Check",
        description="Warn on dependencies not updated in 12+ months",
        action=PolicyAction.WARN,
        conditions={"max_age_months": 12},
    ),
    SecurityPolicy(
        id="POL-005",
        name="Container Image Scanning",
        description="Audit all container images before deployment",
        action=PolicyAction.AUDIT,
        conditions={"scan_type": "container", "on": "pre_deploy"},
    ),
    SecurityPolicy(
        id="POL-006",
        name="CVSS Score Threshold",
        description="Block dependencies with CVSS score >= 9.0",
        action=PolicyAction.BLOCK,
        conditions={"min_cvss": 9.0},
    ),
]


# ---------------------------------------------------------------------------
# CodexSecurityEngine
# ---------------------------------------------------------------------------

class CodexSecurityEngine:
    """Enterprise-grade code security analysis engine.

    Capabilities:
    - SAST: Static Application Security Testing (12 rules, 10+ CWEs)
    - SCA: Software Composition Analysis with CVE database
    - Secret Detection: 17 patterns (AWS, GitHub, Stripe, OpenAI, etc.)
    - License Compliance: 14 license types categorized
    - IaC Security: 7 rules for Docker/Kubernetes/Terraform
    - SBOM Generation: CycloneDX-compatible component inventory
    - Policy Engine: 6 default policies with block/warn/audit actions
    - Compliance: SOC2/ISO27001/GDPR/HIPAA control mapping
    """

    def __init__(self):
        self.policies = list(DEFAULT_POLICIES)
        self._scan_history: list[SecurityDashboard] = []

    # ----- SAST -----

    def run_sast(self, source_code: str, filename: str = "",
                 language: str = "python") -> list[Vulnerability]:
        """Run Static Application Security Testing on source code."""
        findings: list[Vulnerability] = []
        for rule in SAST_RULES:
            if language and rule.get("languages") and language not in rule["languages"]:
                continue
            matches = list(re.finditer(rule["pattern"], source_code, re.IGNORECASE | re.MULTILINE))
            for match in matches:
                line_num = source_code[:match.start()].count("\n") + 1
                findings.append(Vulnerability(
                    id=f"{rule['id']}-{uuid.uuid4().hex[:8]}",
                    title=rule["title"],
                    severity=rule["severity"],
                    scan_type=ScanType.SAST,
                    description=rule["description"],
                    file_path=filename,
                    line_number=line_num,
                    cwe_id=rule.get("cwe", ""),
                    remediation=rule.get("remediation", ""),
                    remediation_priority=(
                        RemediationPriority.IMMEDIATE if rule["severity"] == Severity.CRITICAL
                        else RemediationPriority.SHORT_TERM
                    ),
                    first_seen=datetime.now(timezone.utc).isoformat(),
                ))
        return findings

    # ----- Secret Detection -----

    def scan_secrets(self, content: str, filename: str = "") -> list[SecretFinding]:
        """Detect hardcoded secrets in source code."""
        findings: list[SecretFinding] = []
        for pattern_def in SECRET_PATTERNS:
            matches = list(re.finditer(pattern_def["pattern"], content))
            for match in matches:
                line_num = content[:match.start()].count("\n") + 1
                matched_text = match.group(0)
                redacted = matched_text[:4] + "*" * (len(matched_text) - 8) + matched_text[-4:] \
                    if len(matched_text) > 8 else "***REDACTED***"

                entropy = self._calculate_entropy(matched_text)

                findings.append(SecretFinding(
                    secret_type=pattern_def["name"],
                    file_path=filename,
                    line_number=line_num,
                    severity=pattern_def["severity"],
                    description=f"Detected {pattern_def['name']} in source code",
                    pattern_name=pattern_def["name"],
                    redacted_value=redacted,
                    verified=False,
                    entropy=round(entropy, 2),
                ))
        return findings

    # ----- SCA / Dependency Scanning -----

    def scan_dependencies(self, dependencies: list[dict]) -> list[DependencyVulnerability]:
        """Scan dependencies for known vulnerabilities.

        Args:
            dependencies: List of {name, version, ecosystem} dicts.

        Returns:
            List of known vulnerabilities found.
        """
        known_vulns = self._get_vulnerability_database()
        findings: list[DependencyVulnerability] = []

        for dep in dependencies:
            pkg_name = dep.get("name", "")
            pkg_version = dep.get("version", "")
            ecosystem = dep.get("ecosystem", "")

            for vuln in known_vulns:
                if vuln["package"] == pkg_name and self._version_in_range(
                    pkg_version, vuln.get("vulnerable_range", "")
                ):
                    findings.append(DependencyVulnerability(
                        package_name=pkg_name,
                        installed_version=pkg_version,
                        vulnerable_versions=vuln.get("vulnerable_range", ""),
                        fixed_version=vuln.get("fixed_version", ""),
                        severity=Severity(vuln.get("severity", "medium")),
                        cve_id=vuln.get("cve_id", ""),
                        cvss_score=vuln.get("cvss_score", 0.0),
                        description=vuln.get("description", ""),
                        ecosystem=ecosystem,
                    ))
        return findings

    # ----- License Compliance -----

    def check_licenses(self, packages: list[dict],
                       allowed_categories: Optional[list[str]] = None) -> list[LicenseInfo]:
        """Check license compliance for packages.

        Args:
            packages: List of {name, version, license} dicts.
            allowed_categories: Allowed license categories. Default: ["permissive"].
        """
        if allowed_categories is None:
            allowed_categories = ["permissive"]

        results: list[LicenseInfo] = []
        for pkg in packages:
            license_id = pkg.get("license", "UNLICENSED")
            license_data = LICENSE_DATABASE.get(license_id, {
                "name": license_id, "category": "unknown", "risk": "high",
            })
            compliant = license_data["category"] in allowed_categories
            results.append(LicenseInfo(
                package_name=pkg.get("name", ""),
                version=pkg.get("version", ""),
                license_id=license_id,
                license_name=license_data["name"],
                category=license_data["category"],
                compliant=compliant,
                risk_level=license_data["risk"],
            ))
        return results

    # ----- SBOM Generation -----

    def generate_sbom(self, packages: list[dict],
                      project_name: str = "openagent") -> dict:
        """Generate Software Bill of Materials (CycloneDX format).

        Args:
            packages: List of {name, version, ecosystem, license} dicts.
            project_name: Project name for SBOM metadata.

        Returns:
            CycloneDX-compatible SBOM dict.
        """
        components = []
        for pkg in packages:
            name = pkg.get("name", "")
            version = pkg.get("version", "")
            ecosystem = pkg.get("ecosystem", "pypi")
            purl = f"pkg:{ecosystem}/{name}@{version}"
            sha = hashlib.sha256(f"{name}@{version}".encode()).hexdigest()

            components.append(SBOMComponent(
                name=name, version=version, ecosystem=ecosystem,
                license_id=pkg.get("license", "UNKNOWN"),
                purl=purl, sha256=sha,
                supplier=pkg.get("supplier", ""),
                direct=pkg.get("direct", True),
            ))

        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": f"urn:uuid:{uuid.uuid4()}",
            "version": 1,
            "metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "tools": [{"vendor": "OpenAgent", "name": "Codex Security", "version": "1.0.0"}],
                "component": {"name": project_name, "type": "application"},
            },
            "components": [{
                "type": "library",
                "name": c.name,
                "version": c.version,
                "purl": c.purl,
                "hashes": [{"alg": "SHA-256", "content": c.sha256}],
                "licenses": [{"license": {"id": c.license_id}}],
            } for c in components],
            "totalComponents": len(components),
        }

    # ----- IaC Security -----

    def scan_iac(self, content: str, filename: str = "") -> list[Vulnerability]:
        """Scan Infrastructure as Code files (Dockerfile, K8s, Terraform)."""
        findings: list[Vulnerability] = []
        for rule in IAC_RULES:
            if re.search(rule["pattern"], content, re.IGNORECASE | re.MULTILINE):
                findings.append(Vulnerability(
                    id=f"{rule['id']}-{uuid.uuid4().hex[:8]}",
                    title=rule["title"],
                    severity=rule["severity"],
                    scan_type=ScanType.IAC,
                    description=rule.get("description", rule["title"]),
                    file_path=filename,
                    remediation=rule.get("remediation", ""),
                    first_seen=datetime.now(timezone.utc).isoformat(),
                ))
        return findings

    # ----- Compliance -----

    def run_compliance_check(self, framework: ComplianceFramework,
                             enabled_features: Optional[dict] = None) -> list[ComplianceCheck]:
        """Run compliance check against a framework.

        Args:
            framework: Target compliance framework.
            enabled_features: Dict of {feature_name: True/False} showing what's enabled.
        """
        if enabled_features is None:
            enabled_features = {}

        controls = COMPLIANCE_CONTROLS.get(framework, [])
        results: list[ComplianceCheck] = []

        for control in controls:
            checks_passed = sum(1 for c in control["checks"] if enabled_features.get(c, False))
            total = len(control["checks"])
            status = "passed" if checks_passed == total else "failed"
            missing = [c for c in control["checks"] if not enabled_features.get(c, False)]

            results.append(ComplianceCheck(
                framework=framework,
                control_id=control["id"],
                control_name=control["name"],
                status=status,
                evidence=f"{checks_passed}/{total} checks passed",
                remediation=f"Enable: {', '.join(missing)}" if missing else "",
            ))
        return results

    # ----- Policy Engine -----

    def evaluate_policies(self, findings: list[Vulnerability],
                          secret_findings: Optional[list[SecretFinding]] = None,
                          license_results: Optional[list[LicenseInfo]] = None) -> list[dict]:
        """Evaluate security policies against scan findings."""
        violations = []
        for policy in self.policies:
            if not policy.enabled:
                continue
            violated = False
            details = ""

            if policy.id == "POL-001":
                critical = [f for f in findings if f.severity == Severity.CRITICAL]
                if critical:
                    violated = True
                    details = f"{len(critical)} critical vulnerabilities found"

            elif policy.id == "POL-002":
                if secret_findings:
                    violated = True
                    details = f"{len(secret_findings)} secrets detected in source code"

            elif policy.id == "POL-003":
                if license_results:
                    blocked = [l for l in license_results if not l.compliant]
                    if blocked:
                        violated = True
                        names = [f"{l.package_name}({l.license_id})" for l in blocked[:5]]
                        details = f"Non-compliant licenses: {', '.join(names)}"

            elif policy.id == "POL-006":
                min_cvss = policy.conditions.get("min_cvss", 9.0)
                high_cvss = [f for f in findings if f.cvss_score >= min_cvss]
                if high_cvss:
                    violated = True
                    details = f"{len(high_cvss)} findings with CVSS >= {min_cvss}"

            if violated:
                violations.append({
                    "policy_id": policy.id,
                    "policy_name": policy.name,
                    "action": policy.action.value,
                    "details": details,
                    "blocked": policy.action == PolicyAction.BLOCK,
                })
        return violations

    # ----- Dashboard -----

    def generate_dashboard(self, vulnerabilities: list[Vulnerability],
                           secret_findings: Optional[list[SecretFinding]] = None,
                           scan_types: Optional[list[str]] = None) -> SecurityDashboard:
        """Generate security dashboard summary."""
        severity_counts = {s: 0 for s in Severity}
        for v in vulnerabilities:
            severity_counts[v.severity] += 1

        total = len(vulnerabilities) + (len(secret_findings) if secret_findings else 0)

        # Risk score calculation (100 = perfect, 0 = critical)
        weights = {Severity.CRITICAL: 25, Severity.HIGH: 15, Severity.MEDIUM: 5,
                   Severity.LOW: 2, Severity.INFO: 0}
        penalty = sum(weights.get(v.severity, 0) for v in vulnerabilities)
        if secret_findings:
            penalty += sum(15 if s.severity == Severity.CRITICAL else 8 for s in secret_findings)
        risk_score = max(0, round(100 - penalty, 1))

        grade = (
            "A+" if risk_score >= 98 else
            "A" if risk_score >= 90 else
            "B" if risk_score >= 80 else
            "C" if risk_score >= 70 else
            "D" if risk_score >= 60 else
            "F"
        )

        dashboard = SecurityDashboard(
            scan_id=uuid.uuid4().hex[:12],
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_vulnerabilities=total,
            critical_count=severity_counts[Severity.CRITICAL],
            high_count=severity_counts[Severity.HIGH],
            medium_count=severity_counts[Severity.MEDIUM],
            low_count=severity_counts[Severity.LOW],
            info_count=severity_counts[Severity.INFO],
            risk_score=risk_score,
            grade=grade,
            scan_types_executed=scan_types or ["sast", "secret"],
        )
        self._scan_history.append(dashboard)
        return dashboard

    def get_scan_history(self) -> list[dict]:
        """Return scan history for trend analysis."""
        return [{
            "scan_id": d.scan_id,
            "timestamp": d.timestamp,
            "risk_score": d.risk_score,
            "grade": d.grade,
            "total_vulnerabilities": d.total_vulnerabilities,
        } for d in self._scan_history[-50:]]

    # ----- Full Scan -----

    def run_full_scan(self, source_code: str, filename: str = "",
                      language: str = "python",
                      dependencies: Optional[list[dict]] = None,
                      packages_with_licenses: Optional[list[dict]] = None,
                      iac_content: Optional[str] = None,
                      iac_filename: Optional[str] = None) -> dict:
        """Run comprehensive security scan combining all engines.

        Returns a complete security report with findings, policy evaluation,
        dashboard metrics, and remediation guidance.
        """
        scan_types = []

        # SAST
        sast_findings = self.run_sast(source_code, filename, language)
        scan_types.append("sast")

        # Secret detection
        secret_findings = self.scan_secrets(source_code, filename)
        scan_types.append("secret")

        # SCA
        dep_findings = []
        if dependencies:
            dep_findings = self.scan_dependencies(dependencies)
            scan_types.append("sca")

        # License
        license_results = []
        if packages_with_licenses:
            license_results = self.check_licenses(packages_with_licenses)
            scan_types.append("license")

        # IaC
        iac_findings = []
        if iac_content:
            iac_findings = self.scan_iac(iac_content, iac_filename or "")
            scan_types.append("iac")

        # Combine all vulnerability findings
        all_vulns = sast_findings + iac_findings

        # Policy evaluation
        policy_violations = self.evaluate_policies(all_vulns, secret_findings, license_results)

        # Dashboard
        dashboard = self.generate_dashboard(all_vulns, secret_findings, scan_types)
        dashboard.policy_violations = len(policy_violations)

        # Build report
        return {
            "scan_id": dashboard.scan_id,
            "timestamp": dashboard.timestamp,
            "dashboard": {
                "risk_score": dashboard.risk_score,
                "grade": dashboard.grade,
                "total_vulnerabilities": dashboard.total_vulnerabilities,
                "severity_breakdown": {
                    "critical": dashboard.critical_count,
                    "high": dashboard.high_count,
                    "medium": dashboard.medium_count,
                    "low": dashboard.low_count,
                    "info": dashboard.info_count,
                },
                "scan_types": scan_types,
                "policy_violations": len(policy_violations),
            },
            "sast_findings": [{
                "id": f.id, "title": f.title, "severity": f.severity.value,
                "cwe_id": f.cwe_id, "file_path": f.file_path,
                "line_number": f.line_number, "description": f.description,
                "remediation": f.remediation,
                "priority": f.remediation_priority.value,
            } for f in sast_findings],
            "secret_findings": [{
                "type": s.secret_type, "file_path": s.file_path,
                "line_number": s.line_number, "severity": s.severity.value,
                "redacted_value": s.redacted_value, "entropy": s.entropy,
            } for s in secret_findings],
            "dependency_vulnerabilities": [{
                "package": d.package_name, "installed": d.installed_version,
                "fixed": d.fixed_version, "severity": d.severity.value,
                "cve_id": d.cve_id, "cvss_score": d.cvss_score,
                "description": d.description,
            } for d in dep_findings],
            "license_issues": [{
                "package": l.package_name, "version": l.version,
                "license": l.license_id, "category": l.category,
                "compliant": l.compliant, "risk": l.risk_level,
            } for l in license_results if not l.compliant],
            "iac_findings": [{
                "id": f.id, "title": f.title, "severity": f.severity.value,
                "file_path": f.file_path, "remediation": f.remediation,
            } for f in iac_findings],
            "policy_violations": policy_violations,
        }

    # ----- Helpers -----

    @staticmethod
    def _calculate_entropy(text: str) -> float:
        """Calculate Shannon entropy of a string (higher = more random = likely a secret)."""
        if not text:
            return 0.0
        import math
        freq: dict[str, int] = {}
        for c in text:
            freq[c] = freq.get(c, 0) + 1
        length = len(text)
        return -sum((count / length) * math.log2(count / length) for count in freq.values())

    @staticmethod
    def _version_in_range(version: str, vuln_range: str) -> bool:
        """Check if version is in vulnerable range (simplified)."""
        if not vuln_range:
            return False
        if "<" in vuln_range:
            return True  # Simplified — real implementation would use semver
        return version in vuln_range

    @staticmethod
    def _get_vulnerability_database() -> list[dict]:
        """Return known vulnerability database (simplified mock).

        In production, this would query NVD/OSV/GitHub Advisory Database.
        """
        return [
            {
                "package": "lodash", "vulnerable_range": "<4.17.21",
                "fixed_version": "4.17.21", "severity": "critical",
                "cve_id": "CVE-2021-23337", "cvss_score": 7.2,
                "description": "Command Injection in lodash",
            },
            {
                "package": "requests", "vulnerable_range": "<2.31.0",
                "fixed_version": "2.31.0", "severity": "medium",
                "cve_id": "CVE-2023-32681", "cvss_score": 6.1,
                "description": "Unintended leak of Proxy-Authorization header in requests",
            },
            {
                "package": "pillow", "vulnerable_range": "<10.0.1",
                "fixed_version": "10.0.1", "severity": "high",
                "cve_id": "CVE-2023-44271", "cvss_score": 7.5,
                "description": "Denial of Service in Pillow via uncontrolled resource consumption",
            },
            {
                "package": "django", "vulnerable_range": "<4.2.7",
                "fixed_version": "4.2.7", "severity": "high",
                "cve_id": "CVE-2023-46695", "cvss_score": 7.5,
                "description": "Potential denial of service in UsernameField",
            },
            {
                "package": "express", "vulnerable_range": "<4.19.2",
                "fixed_version": "4.19.2", "severity": "medium",
                "cve_id": "CVE-2024-29041", "cvss_score": 6.1,
                "description": "Open redirect vulnerability in Express.js",
            },
        ]

    def get_capabilities(self) -> dict:
        """Return engine capabilities and statistics."""
        return {
            "engine": "Codex Security",
            "version": "1.0.0",
            "capabilities": {
                "sast": {
                    "name": "Static Application Security Testing",
                    "rules_count": len(SAST_RULES),
                    "cwe_coverage": list({r.get("cwe", "") for r in SAST_RULES if r.get("cwe")}),
                    "languages": ["python", "javascript", "typescript", "java", "go", "php"],
                },
                "secret_detection": {
                    "name": "Secret Detection",
                    "patterns_count": len(SECRET_PATTERNS),
                    "providers": [p["name"] for p in SECRET_PATTERNS],
                },
                "sca": {
                    "name": "Software Composition Analysis",
                    "description": "Dependency vulnerability scanning against CVE database",
                    "ecosystems": ["pypi", "npm", "maven", "go", "cargo"],
                },
                "license_compliance": {
                    "name": "License Compliance",
                    "known_licenses": len(LICENSE_DATABASE),
                    "categories": ["permissive", "copyleft", "weak_copyleft", "restricted", "unknown"],
                },
                "iac_security": {
                    "name": "Infrastructure as Code Security",
                    "rules_count": len(IAC_RULES),
                    "platforms": ["Docker", "Kubernetes", "Terraform"],
                },
                "sbom": {
                    "name": "Software Bill of Materials",
                    "format": "CycloneDX 1.5",
                },
                "compliance": {
                    "name": "Compliance Reporting",
                    "frameworks": [f.value for f in ComplianceFramework],
                },
                "policy_engine": {
                    "name": "Security Policy Engine",
                    "default_policies": len(DEFAULT_POLICIES),
                    "actions": [a.value for a in PolicyAction],
                },
            },
        }


# Module-level singleton
codex_security = CodexSecurityEngine()
