"""安全服务 / Security service.

基于 OWASP LLM Top 10 的安全检查和防护。
参考规划文档中行业标准分析。
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityCheck:
    id: str
    name: str
    owasp_ref: str
    description: str
    risk_level: RiskLevel
    passed: bool = True
    details: str = ""


@dataclass
class SecurityReport:
    timestamp: str = ""
    total_checks: int = 0
    passed: int = 0
    failed: int = 0
    risk_score: float = 0.0
    checks: list = field(default_factory=list)

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


# OWASP LLM Top 10 (2025) 检查规则
OWASP_RULES = [
    {
        "id": "LLM01",
        "name": "Prompt Injection",
        "owasp_ref": "OWASP-LLM01",
        "description": "防止提示注入攻击",
        "patterns": [
            r"ignore\s+(previous|all)\s+\w*\s*(instructions|prompts)",
            r"system\s*:\s*you\s+are\s+now",
            r"forget\s+(everything|all|your)",
            r"new\s+instructions?\s*:",
            r"override\s+(system|instructions)",
            r"\\x[0-9a-f]{2}",  # hex escape sequences
        ],
    },
    {
        "id": "LLM02",
        "name": "Insecure Output Handling",
        "owasp_ref": "OWASP-LLM02",
        "description": "防止不安全的输出处理",
        "patterns": [
            r"<script[\s>]",
            r"javascript\s*:",
            r"on\w+\s*=\s*['\"]",
            r"eval\s*\(",
            r"exec\s*\(",
        ],
    },
    {
        "id": "LLM06",
        "name": "Sensitive Information Disclosure",
        "owasp_ref": "OWASP-LLM06",
        "description": "防止敏感信息泄露",
        "patterns": [
            r"(?:api[_-]?key|secret[_-]?key|password|token)\s*[=:]\s*['\"][^'\"]{8,}",
            r"(?:aws|azure|gcp)_(?:access|secret)_key",
            r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----",
            r"(?:mysql|postgres|mongodb)://\w+:\w+@",
        ],
    },
    {
        "id": "LLM07",
        "name": "System Prompt Leakage",
        "owasp_ref": "OWASP-LLM07",
        "description": "防止系统提示泄露",
        "patterns": [
            r"(?:show|print|display|reveal|output)\s+(?:your\s+)?(?:system\s+)?prompt",
            r"what\s+(?:is|are)\s+your\s+(?:system\s+)?(?:instructions|rules)",
            r"repeat\s+(?:the\s+)?(?:above|system)\s+(?:text|message|prompt)",
        ],
    },
]

DANGEROUS_COMMANDS = [
    r"rm\s+-rf\s+/",
    r"rm\s+-rf\s+\*",
    r"mkfs\.",
    r"dd\s+if=.*of=/dev/",
    r":\(\)\s*\{\s*:\|:\s*&\s*\}\s*;",  # fork bomb
    r"chmod\s+-R\s+777\s+/",
    r"DROP\s+(?:TABLE|DATABASE)",
    r"DELETE\s+FROM\s+\w+\s*;?\s*$",  # DELETE without WHERE
    r"TRUNCATE\s+TABLE",
    r"curl.*\|\s*(?:bash|sh)",
    r"wget.*\|\s*(?:bash|sh)",
    r">\s*/dev/sd[a-z]",
    r"sudo\s+passwd\s+root",
]

SENSITIVE_FILE_PATTERNS = [
    r"\.env$",
    r"\.env\.local$",
    r"\.env\.production$",
    r"credentials\.json$",
    r"id_rsa$",
    r"id_ed25519$",
    r"\.pem$",
    r"\.key$",
    r"\.keystore$",
    r"\.jks$",
    r"\.p12$",
    r"\.pfx$",
    r"secrets?\.(ya?ml|json|toml)$",
    r"\.htpasswd$",
    r"shadow$",
    r"passwd$",
]


class SecurityService:
    """OWASP LLM Top 10 安全检查服务."""

    def check_prompt_injection(self, text: str) -> SecurityCheck:
        rule = OWASP_RULES[0]
        check = SecurityCheck(
            id=rule["id"],
            name=rule["name"],
            owasp_ref=rule["owasp_ref"],
            description=rule["description"],
            risk_level=RiskLevel.CRITICAL,
        )
        for pattern in rule["patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                check.passed = False
                check.details = f"Detected prompt injection pattern: {pattern}"
                break
        return check

    def check_output_safety(self, text: str) -> SecurityCheck:
        rule = OWASP_RULES[1]
        check = SecurityCheck(
            id=rule["id"],
            name=rule["name"],
            owasp_ref=rule["owasp_ref"],
            description=rule["description"],
            risk_level=RiskLevel.HIGH,
        )
        for pattern in rule["patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                check.passed = False
                check.details = f"Unsafe output pattern: {pattern}"
                break
        return check

    def check_sensitive_info(self, text: str) -> SecurityCheck:
        rule = OWASP_RULES[2]
        check = SecurityCheck(
            id=rule["id"],
            name=rule["name"],
            owasp_ref=rule["owasp_ref"],
            description=rule["description"],
            risk_level=RiskLevel.HIGH,
        )
        for pattern in rule["patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                check.passed = False
                check.details = f"Sensitive info pattern detected: {pattern}"
                break
        return check

    def check_system_prompt_leakage(self, text: str) -> SecurityCheck:
        rule = OWASP_RULES[3]
        check = SecurityCheck(
            id=rule["id"],
            name=rule["name"],
            owasp_ref=rule["owasp_ref"],
            description=rule["description"],
            risk_level=RiskLevel.MEDIUM,
        )
        for pattern in rule["patterns"]:
            if re.search(pattern, text, re.IGNORECASE):
                check.passed = False
                check.details = f"System prompt leakage attempt: {pattern}"
                break
        return check

    def check_dangerous_command(self, command: str) -> SecurityCheck:
        check = SecurityCheck(
            id="CMD01",
            name="Dangerous Command",
            owasp_ref="OWASP-LLM02/LLM05",
            description="检测危险系统命令",
            risk_level=RiskLevel.CRITICAL,
        )
        for pattern in DANGEROUS_COMMANDS:
            if re.search(pattern, command, re.IGNORECASE):
                check.passed = False
                check.details = f"Dangerous command blocked: {pattern}"
                break
        return check

    def check_sensitive_file(self, filepath: str) -> SecurityCheck:
        check = SecurityCheck(
            id="FILE01",
            name="Sensitive File Access",
            owasp_ref="OWASP-LLM06",
            description="检测敏感文件访问",
            risk_level=RiskLevel.HIGH,
        )
        for pattern in SENSITIVE_FILE_PATTERNS:
            if re.search(pattern, filepath, re.IGNORECASE):
                check.passed = False
                check.details = f"Access to sensitive file blocked: {filepath}"
                break
        return check

    def run_full_scan(self, text: str) -> SecurityReport:
        checks = [
            self.check_prompt_injection(text),
            self.check_output_safety(text),
            self.check_sensitive_info(text),
            self.check_system_prompt_leakage(text),
        ]
        report = SecurityReport(
            total_checks=len(checks),
            passed=sum(1 for c in checks if c.passed),
            failed=sum(1 for c in checks if not c.passed),
            checks=[{
                "id": c.id,
                "name": c.name,
                "owasp_ref": c.owasp_ref,
                "risk_level": c.risk_level.value,
                "passed": c.passed,
                "details": c.details,
            } for c in checks],
        )
        # risk score: 0-100
        weight = {"critical": 40, "high": 25, "medium": 15, "low": 5}
        max_score = sum(weight.get(c.risk_level.value, 5) for c in checks)
        lost = sum(weight.get(c.risk_level.value, 5) for c in checks if not c.passed)
        report.risk_score = round((1 - lost / max_score) * 100, 1) if max_score else 100.0
        return report

    def get_owasp_rules(self) -> list[dict]:
        return [{
            "id": r["id"],
            "name": r["name"],
            "owasp_ref": r["owasp_ref"],
            "description": r["description"],
            "pattern_count": len(r["patterns"]),
        } for r in OWASP_RULES]


security_service = SecurityService()
