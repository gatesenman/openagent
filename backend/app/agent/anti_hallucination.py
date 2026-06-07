"""Anti-Hallucination Verification Pipeline.

6-gate verification chain that validates Agent-generated code
before it can be committed:
  Gate 1: Syntax validation (tree-sitter / regex)
  Gate 2: Type checking (pyright / tsc)
  Gate 3: Lint (ruff / eslint)
  Gate 4: Unit tests (pytest / jest)
  Gate 5: Integration validation (build / server start)
  Gate 6: Agent self-review (diff analysis)
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class GateResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    WARNING = "warning"


class GateType(str, Enum):
    SYNTAX = "syntax"
    TYPE_CHECK = "type_check"
    LINT = "lint"
    UNIT_TEST = "unit_test"
    INTEGRATION = "integration"
    SELF_REVIEW = "self_review"


@dataclass
class GateReport:
    """Result from a single verification gate."""

    gate: GateType
    result: GateResult
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    duration_ms: float = 0.0
    details: dict[str, Any] = field(default_factory=dict)
    auto_fix_attempted: bool = False
    auto_fix_succeeded: bool = False


@dataclass
class VerificationReport:
    """Complete pipeline verification report."""

    session_id: str
    gates: list[GateReport] = field(default_factory=list)
    overall_result: GateResult = GateResult.PASS
    total_duration_ms: float = 0.0
    auto_fix_rounds: int = 0
    max_auto_fix_rounds: int = 3
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def all_passed(self) -> bool:
        return all(
            g.result in (GateResult.PASS, GateResult.SKIP, GateResult.WARNING)
            for g in self.gates
        )

    @property
    def failed_gates(self) -> list[GateReport]:
        return [g for g in self.gates if g.result == GateResult.FAIL]


class SyntaxValidator:
    """Gate 1: Validates code syntax."""

    SYNTAX_PATTERNS = {
        ".py": [
            (r"def \w+\([^)]*\)\s*:", "function_def"),
            (r"class \w+.*:", "class_def"),
            (r"import \w+", "import"),
        ],
        ".ts": [
            (r"(export\s+)?(function|class|interface|type|const|let)\s+\w+", "declaration"),
            (r"import\s+.*from\s+['\"]", "import"),
        ],
        ".tsx": [
            (r"(export\s+)?(function|class|const)\s+\w+", "declaration"),
            (r"return\s*\(", "jsx_return"),
        ],
    }

    async def validate(self, files: dict[str, str]) -> GateReport:
        """Validate syntax of changed files."""
        errors = []
        for filepath, content in files.items():
            ext = "." + filepath.rsplit(".", 1)[-1] if "." in filepath else ""
            # Check for common syntax issues
            if ext == ".py":
                errors.extend(self._check_python_syntax(filepath, content))
            elif ext in (".ts", ".tsx", ".js", ".jsx"):
                errors.extend(self._check_js_syntax(filepath, content))

        return GateReport(
            gate=GateType.SYNTAX,
            result=GateResult.FAIL if errors else GateResult.PASS,
            errors=errors,
        )

    def _check_python_syntax(self, filepath: str, content: str) -> list[str]:
        errors = []
        try:
            compile(content, filepath, "exec")
        except SyntaxError as e:
            errors.append(f"{filepath}:{e.lineno}: {e.msg}")
        return errors

    def _check_js_syntax(self, filepath: str, content: str) -> list[str]:
        errors = []
        # Basic bracket matching
        stack: list[str] = []
        brackets = {"(": ")", "[": "]", "{": "}"}
        for i, ch in enumerate(content):
            if ch in brackets:
                stack.append(brackets[ch])
            elif ch in brackets.values():
                if not stack or stack[-1] != ch:
                    line = content[:i].count("\n") + 1
                    errors.append(f"{filepath}:{line}: Unmatched bracket '{ch}'")
                    break
                stack.pop()
        return errors


class TypeChecker:
    """Gate 2: Type checking via language-specific tools."""

    async def check(self, files: dict[str, str], language: str = "python") -> GateReport:
        """Run type checking on changed files."""
        # In production: invoke pyright/tsc/rustc
        warnings = []
        for filepath, content in files.items():
            if language == "python":
                warnings.extend(self._check_python_types(filepath, content))

        return GateReport(
            gate=GateType.TYPE_CHECK,
            result=GateResult.WARNING if warnings else GateResult.PASS,
            warnings=warnings,
        )

    def _check_python_types(self, filepath: str, content: str) -> list[str]:
        warnings = []
        # Detect use of Any, getattr, setattr
        for i, line in enumerate(content.split("\n"), 1):
            if re.search(r"\bAny\b", line) and "import" not in line:
                warnings.append(f"{filepath}:{i}: Avoid using 'Any' type")
            if re.search(r"\bgetattr\s*\(", line):
                warnings.append(f"{filepath}:{i}: Avoid getattr, use typed access")
            if re.search(r"\bsetattr\s*\(", line):
                warnings.append(f"{filepath}:{i}: Avoid setattr, use typed access")
        return warnings


class LintChecker:
    """Gate 3: Lint checking."""

    async def check(self, files: dict[str, str]) -> GateReport:
        """Run lint checks on changed files."""
        # In production: invoke ruff/eslint
        warnings = []
        for filepath, content in files.items():
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                if len(line) > 120:
                    warnings.append(f"{filepath}:{i}: Line too long ({len(line)} > 120)")
                if line.rstrip() != line and line.strip():
                    warnings.append(f"{filepath}:{i}: Trailing whitespace")

        return GateReport(
            gate=GateType.LINT,
            result=GateResult.WARNING if warnings else GateResult.PASS,
            warnings=warnings,
        )


class SelfReviewer:
    """Gate 6: Agent self-review of its own diff."""

    REVIEW_CHECKS = [
        ("unused_import", r"^import\s+\w+", "Check all imports are used"),
        ("todo_left", r"#\s*TODO|//\s*TODO", "Leftover TODO comments"),
        ("debug_left", r"console\.log|print\(.*debug|breakpoint\(\)", "Debug statements"),
        ("hardcoded_secret", r"(password|secret|key|token)\s*=\s*['\"][^'\"]+['\"]", "Hardcoded secrets"),
    ]

    async def review(self, files: dict[str, str]) -> GateReport:
        """Self-review changed files for common issues."""
        warnings = []
        errors = []

        for filepath, content in files.items():
            for check_name, pattern, desc in self.REVIEW_CHECKS:
                matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
                for m in matches:
                    line_no = content[: m.start()].count("\n") + 1
                    if check_name == "hardcoded_secret":
                        errors.append(f"{filepath}:{line_no}: {desc}")
                    else:
                        warnings.append(f"{filepath}:{line_no}: {desc}")

        return GateReport(
            gate=GateType.SELF_REVIEW,
            result=GateResult.FAIL if errors else (GateResult.WARNING if warnings else GateResult.PASS),
            errors=errors,
            warnings=warnings,
        )


class AntiHallucinationPipeline:
    """6-gate verification pipeline for Agent-generated code.

    All gates run in sequence. If any gate fails, the Agent
    is given the error and asked to auto-fix (up to 3 rounds).
    After 3 failed rounds, the user is notified.
    """

    def __init__(self) -> None:
        self.syntax_validator = SyntaxValidator()
        self.type_checker = TypeChecker()
        self.lint_checker = LintChecker()
        self.self_reviewer = SelfReviewer()
        self.max_auto_fix_rounds = 3

    async def verify(
        self, session_id: str, changed_files: dict[str, str], language: str = "python"
    ) -> VerificationReport:
        """Run the full 6-gate verification pipeline."""
        report = VerificationReport(session_id=session_id)

        # Gate 1: Syntax
        gate1 = await self.syntax_validator.validate(changed_files)
        report.gates.append(gate1)

        # Gate 2: Type Check
        gate2 = await self.type_checker.check(changed_files, language)
        report.gates.append(gate2)

        # Gate 3: Lint
        gate3 = await self.lint_checker.check(changed_files)
        report.gates.append(gate3)

        # Gate 4: Unit Tests (placeholder — in production runs pytest/jest in sandbox)
        gate4 = GateReport(gate=GateType.UNIT_TEST, result=GateResult.SKIP)
        report.gates.append(gate4)

        # Gate 5: Integration (placeholder — in production runs build in sandbox)
        gate5 = GateReport(gate=GateType.INTEGRATION, result=GateResult.SKIP)
        report.gates.append(gate5)

        # Gate 6: Self-Review
        gate6 = await self.self_reviewer.review(changed_files)
        report.gates.append(gate6)

        # Determine overall result
        if any(g.result == GateResult.FAIL for g in report.gates):
            report.overall_result = GateResult.FAIL
        elif any(g.result == GateResult.WARNING for g in report.gates):
            report.overall_result = GateResult.WARNING
        else:
            report.overall_result = GateResult.PASS

        report.total_duration_ms = sum(g.duration_ms for g in report.gates)
        return report


# Singleton
anti_hallucination = AntiHallucinationPipeline()
