"""PR Review 引擎 / PR Review Engine.

自动审查 Pull Request:
- 代码质量分析 (复杂度/重复/安全)
- 变更风险评估
- 评论生成 (Bug/Flag/Note 三级)
- 规则匹配 (REVIEW.md 文件模式)
"""

import logging
import re
import uuid
import time
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ReviewSeverity(str, Enum):
    BUG = "bug"          # 明确的缺陷
    FLAG = "flag"        # 需要调查
    NOTE = "note"        # 建议改进


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ReviewComment:
    """Review 评论."""
    id: str = ""
    file_path: str = ""
    line: int = 0
    severity: ReviewSeverity = ReviewSeverity.NOTE
    message: str = ""
    suggestion: str = ""  # 建议的修改
    rule: str = ""        # 触发的规则

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


@dataclass
class ReviewResult:
    """PR Review 结果."""
    pr_id: str = ""
    repo: str = ""
    comments: list[ReviewComment] = field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    summary: str = ""
    files_reviewed: int = 0
    issues_found: int = 0
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class ReviewRule:
    """Review 规则."""
    id: str = ""
    pattern: str = ""       # 文件匹配模式 (glob)
    check_type: str = ""    # security / style / complexity / custom
    severity: ReviewSeverity = ReviewSeverity.NOTE
    message: str = ""
    enabled: bool = True

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())


# 内置安全审查规则
BUILTIN_RULES: list[dict] = [
    {
        "pattern": "**/*.py",
        "check_type": "security",
        "severity": "bug",
        "message": "硬编码密钥检测: 发现疑似 API Key 或密码硬编码",
        "regex": r"(?:api_key|password|secret|token)\s*=\s*['\"][^'\"]{8,}['\"]",
    },
    {
        "pattern": "**/*.py",
        "check_type": "security",
        "severity": "flag",
        "message": "使用 eval/exec 存在代码注入风险",
        "regex": r"\beval\s*\(|\bexec\s*\(",
    },
    {
        "pattern": "**/*.py",
        "check_type": "security",
        "severity": "flag",
        "message": "subprocess.shell=True 存在命令注入风险",
        "regex": r"subprocess\.\w+\([^)]*shell\s*=\s*True",
    },
    {
        "pattern": "**/*.{ts,tsx,js,jsx}",
        "check_type": "security",
        "severity": "bug",
        "message": "XSS 风险: 使用 dangerouslySetInnerHTML",
        "regex": r"dangerouslySetInnerHTML",
    },
    {
        "pattern": "**/*.py",
        "check_type": "style",
        "severity": "note",
        "message": "TODO/FIXME 标记: 需要后续处理",
        "regex": r"#\s*(TODO|FIXME|HACK|XXX)",
    },
    {
        "pattern": "**/*.py",
        "check_type": "complexity",
        "severity": "flag",
        "message": "函数过长: 超过 50 行的函数建议拆分",
        "max_lines": 50,
    },
]


class PRReviewService:
    """PR Review 引擎.

    Phase 1: 基于正则/规则的静态分析
    Phase 2: 结合 LLM 进行语义级审查
    """

    def __init__(self):
        self._rules: list[ReviewRule] = []
        self._results: dict[str, ReviewResult] = {}  # pr_id → result
        self._init_builtin_rules()

    def _init_builtin_rules(self):
        for r in BUILTIN_RULES:
            self._rules.append(ReviewRule(
                pattern=r["pattern"],
                check_type=r["check_type"],
                severity=ReviewSeverity(r["severity"]),
                message=r["message"],
            ))

    def review_diff(self, pr_id: str, repo: str, diff_text: str) -> ReviewResult:
        """审查 PR diff."""
        comments: list[ReviewComment] = []
        files_reviewed = 0
        current_file = ""
        current_line = 0

        for line in diff_text.split("\n"):
            if line.startswith("diff --git"):
                files_reviewed += 1
                parts = line.split(" b/")
                current_file = parts[-1] if len(parts) > 1 else ""
                current_line = 0
            elif line.startswith("@@"):
                match = re.search(r"\+(\d+)", line)
                if match:
                    current_line = int(match.group(1))
            elif line.startswith("+") and not line.startswith("+++"):
                added_line = line[1:]
                current_line += 1
                for rule_def in BUILTIN_RULES:
                    regex = rule_def.get("regex")
                    if regex and re.search(regex, added_line, re.IGNORECASE):
                        comments.append(ReviewComment(
                            file_path=current_file,
                            line=current_line,
                            severity=ReviewSeverity(rule_def["severity"]),
                            message=rule_def["message"],
                            rule=rule_def["check_type"],
                        ))
            elif not line.startswith("-"):
                current_line += 1

        risk = self._assess_risk(comments, files_reviewed)
        result = ReviewResult(
            pr_id=pr_id,
            repo=repo,
            comments=comments,
            risk_level=risk,
            summary=self._generate_summary(comments, files_reviewed, risk),
            files_reviewed=files_reviewed,
            issues_found=len(comments),
        )
        self._results[pr_id] = result
        return result

    def _assess_risk(self, comments: list[ReviewComment], files: int) -> RiskLevel:
        """评估变更风险."""
        bugs = sum(1 for c in comments if c.severity == ReviewSeverity.BUG)
        flags = sum(1 for c in comments if c.severity == ReviewSeverity.FLAG)

        if bugs >= 2:
            return RiskLevel.CRITICAL
        if bugs >= 1 or flags >= 3:
            return RiskLevel.HIGH
        if flags >= 1:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _generate_summary(
        self, comments: list[ReviewComment], files: int, risk: RiskLevel
    ) -> str:
        """生成审查摘要."""
        bugs = sum(1 for c in comments if c.severity == ReviewSeverity.BUG)
        flags = sum(1 for c in comments if c.severity == ReviewSeverity.FLAG)
        notes = sum(1 for c in comments if c.severity == ReviewSeverity.NOTE)

        risk_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}
        emoji = risk_emoji.get(risk.value, "⚪")

        return (
            f"{emoji} 风险等级: {risk.value.upper()}\n"
            f"审查文件: {files} | Bug: {bugs} | Flag: {flags} | Note: {notes}\n"
        )

    def get_result(self, pr_id: str) -> ReviewResult | None:
        return self._results.get(pr_id)

    def add_rule(self, rule: ReviewRule):
        self._rules.append(rule)

    def list_rules(self) -> list[dict]:
        return [
            {"id": r.id, "pattern": r.pattern, "check_type": r.check_type,
             "severity": r.severity.value, "enabled": r.enabled}
            for r in self._rules
        ]


pr_review_service = PRReviewService()
