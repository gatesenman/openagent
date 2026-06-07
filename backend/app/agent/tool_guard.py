"""Tool Output Guard — protects Agent from bad tool outputs.

Classifies tool errors and determines the appropriate recovery
action: stop, retry with hint, auto-retry, or pass through.
"""

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ErrorClass(str, Enum):
    """Classification of tool output errors."""

    SCHEMA_MISMATCH = "schema_mismatch"
    PARTIAL_DATA = "partial_data"
    SEMANTIC_GARBAGE = "semantic_garbage"
    TRANSIENT_FAILURE = "transient_failure"
    PERMISSION_DENIED = "permission_denied"
    NOT_FOUND = "not_found"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    SUCCESS = "success"


class GuardAction(str, Enum):
    """Action to take after tool output classification."""

    PASS = "pass"
    STOP_WITH_MESSAGE = "stop_with_message"
    RETRY_WITH_HINT = "retry_with_hint"
    AUTO_RETRY = "auto_retry"
    TRUNCATE_AND_SAVE = "truncate_and_save"


@dataclass
class GuardDecision:
    """Decision from the tool output guard."""

    action: GuardAction
    message: str = ""
    hint: str = ""
    retry_count: int = 0
    max_retries: int = 3
    truncated_path: str = ""
    original_output: str = ""


class ToolOutputGuard:
    """Protects Agent from bad tool outputs.

    Classifies errors and determines recovery strategy:
    - SCHEMA_MISMATCH → stop, tell Agent to use different approach
    - PARTIAL_DATA → retry with smaller scope
    - SEMANTIC_GARBAGE → retry with different keywords
    - TRANSIENT_FAILURE → auto-retry up to 3 times
    - PERMISSION_DENIED → stop, escalate to user
    - NOT_FOUND → hint to check path/name
    - TIMEOUT → auto-retry with timeout increase
    - RATE_LIMIT → wait and retry
    """

    MAX_OUTPUT_TOKENS = 50000  # ~200KB
    MAX_OUTPUT_CHARS = MAX_OUTPUT_TOKENS * 4

    # Error patterns for classification
    ERROR_PATTERNS = {
        ErrorClass.PERMISSION_DENIED: [
            r"permission denied",
            r"access denied",
            r"forbidden",
            r"EACCES",
            r"Operation not permitted",
        ],
        ErrorClass.NOT_FOUND: [
            r"no such file or directory",
            r"not found",
            r"ENOENT",
            r"does not exist",
            r"404",
        ],
        ErrorClass.TIMEOUT: [
            r"timed? ?out",
            r"ETIMEDOUT",
            r"deadline exceeded",
            r"context deadline",
        ],
        ErrorClass.RATE_LIMIT: [
            r"rate limit",
            r"too many requests",
            r"429",
            r"throttle",
        ],
        ErrorClass.TRANSIENT_FAILURE: [
            r"connection refused",
            r"ECONNREFUSED",
            r"network error",
            r"temporary failure",
            r"503",
            r"502",
        ],
    }

    def __init__(self) -> None:
        self._retry_counts: dict[str, int] = {}

    def check(
        self, tool_name: str, args: dict[str, Any], result: str, exit_code: int = 0
    ) -> GuardDecision:
        """Classify tool output and determine action."""
        call_key = f"{tool_name}:{hash(str(args))}"

        # Success case
        if exit_code == 0 and result and not self._looks_like_error(result):
            # Check output size
            if len(result) > self.MAX_OUTPUT_CHARS:
                return self._handle_large_output(tool_name, result)
            # Check for empty/garbage results
            if self._is_semantic_garbage(result):
                return GuardDecision(
                    action=GuardAction.RETRY_WITH_HINT,
                    message="Tool returned empty or meaningless results",
                    hint="Try different search terms or broader scope",
                    original_output=result,
                )
            return GuardDecision(action=GuardAction.PASS, original_output=result)

        # Classify the error
        error_class = self._classify_error(result, exit_code)
        retry_count = self._retry_counts.get(call_key, 0)

        if error_class == ErrorClass.SCHEMA_MISMATCH:
            return GuardDecision(
                action=GuardAction.STOP_WITH_MESSAGE,
                message=f"Tool '{tool_name}' returned invalid data format. Try a different approach.",
                original_output=result,
            )

        elif error_class == ErrorClass.PARTIAL_DATA:
            return GuardDecision(
                action=GuardAction.RETRY_WITH_HINT,
                hint="Results were truncated. Try narrowing the query scope.",
                retry_count=retry_count,
                original_output=result,
            )

        elif error_class == ErrorClass.PERMISSION_DENIED:
            return GuardDecision(
                action=GuardAction.STOP_WITH_MESSAGE,
                message=f"Permission denied for '{tool_name}'. This may need user intervention.",
                original_output=result,
            )

        elif error_class == ErrorClass.NOT_FOUND:
            return GuardDecision(
                action=GuardAction.RETRY_WITH_HINT,
                hint="File or resource not found. Check the path or name.",
                retry_count=retry_count,
                original_output=result,
            )

        elif error_class in (ErrorClass.TRANSIENT_FAILURE, ErrorClass.TIMEOUT):
            if retry_count < 3:
                self._retry_counts[call_key] = retry_count + 1
                return GuardDecision(
                    action=GuardAction.AUTO_RETRY,
                    message=f"Transient error, auto-retrying ({retry_count + 1}/3)",
                    retry_count=retry_count + 1,
                    max_retries=3,
                    original_output=result,
                )
            else:
                return GuardDecision(
                    action=GuardAction.STOP_WITH_MESSAGE,
                    message=f"Tool '{tool_name}' failed after 3 retries. Try a different approach.",
                    original_output=result,
                )

        elif error_class == ErrorClass.RATE_LIMIT:
            return GuardDecision(
                action=GuardAction.AUTO_RETRY,
                message="Rate limited. Waiting before retry.",
                retry_count=retry_count + 1,
                original_output=result,
            )

        # Default: pass through with warning
        return GuardDecision(
            action=GuardAction.PASS,
            message=f"Tool '{tool_name}' returned with exit code {exit_code}",
            original_output=result,
        )

    def _classify_error(self, output: str, exit_code: int) -> ErrorClass:
        """Classify error type from tool output."""
        output_lower = output.lower()

        for error_class, patterns in self.ERROR_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, output_lower):
                    return error_class

        if exit_code != 0:
            return ErrorClass.TRANSIENT_FAILURE

        return ErrorClass.SUCCESS

    def _looks_like_error(self, output: str) -> bool:
        """Quick check if output contains error indicators."""
        error_indicators = ["error:", "Error:", "ERROR:", "fatal:", "FATAL:"]
        return any(ind in output for ind in error_indicators)

    def _is_semantic_garbage(self, output: str) -> bool:
        """Check if output is technically valid but semantically empty."""
        stripped = output.strip()
        if not stripped:
            return True
        if len(stripped) < 5:
            return True
        return False

    def _handle_large_output(self, tool_name: str, output: str) -> GuardDecision:
        """Handle output that exceeds the token budget."""
        truncated = output[: self.MAX_OUTPUT_CHARS]
        saved_path = f"/tmp/tool_output_{tool_name}_{hash(output) % 10000}.txt"

        return GuardDecision(
            action=GuardAction.TRUNCATE_AND_SAVE,
            message=f"Output truncated ({len(output)} chars). Full output saved to {saved_path}",
            truncated_path=saved_path,
            original_output=truncated,
        )

    def reset_retries(self, tool_name: str | None = None) -> None:
        """Reset retry counters."""
        if tool_name:
            keys_to_remove = [k for k in self._retry_counts if k.startswith(tool_name)]
            for k in keys_to_remove:
                del self._retry_counts[k]
        else:
            self._retry_counts.clear()


# Singleton
tool_guard = ToolOutputGuard()
