"""输出验证器 / Output validators.

验证 LLM 输出和工具调用，防止幻觉和危险操作。
零幻觉验证管道的关键组件。
"""

import json
import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)

DANGEROUS_COMMANDS = [
    r"rm\s+-rf\s+/(?:\s|$)",
    r"rm\s+-rf\s+/\*",
    r"mkfs\.\w+",
    r"dd\s+if=.+of=/dev/",
    r">\s*/dev/sd[a-z]",
    r"chmod\s+-R\s+777\s+/\s*$",
    r"DROP\s+DATABASE",
    r"DROP\s+TABLE",
    r"TRUNCATE\s+TABLE",
    r"DELETE\s+FROM\s+\w+\s*;?\s*$",  # DELETE without WHERE
    r"curl\s+.+\|\s*(?:sudo\s+)?bash",
    r"wget\s+.+\|\s*(?:sudo\s+)?bash",
    r":()\s*\{\s*:\|:&\s*\}\s*;",  # fork bomb
]

SENSITIVE_PATTERNS = [
    r"(?:password|passwd|pwd)\s*[:=]\s*['\"]?\S+",
    r"(?:api_?key|apikey|secret_?key)\s*[:=]\s*['\"]?\S+",
    r"(?:token|auth_?token|access_?token)\s*[:=]\s*['\"]?\S+",
    r"-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----",
]


@dataclass
class ValidationResult:
    """验证结果."""
    valid: bool
    errors: list[str]
    warnings: list[str]


class OutputValidator:
    """LLM 输出验证器.

    实现零幻觉验证管道的多层检查：
    1. 工具调用参数验证（JSON Schema）
    2. 危险命令拦截
    3. 敏感信息泄露检测
    4. 输出格式验证
    """

    def validate_tool_call(
        self, tool_name: str, args: dict, tool_schema: dict | None = None
    ) -> ValidationResult:
        """验证工具调用参数."""
        errors: list[str] = []
        warnings: list[str] = []

        # 基本检查
        if not tool_name:
            errors.append("工具名称为空")
        if not isinstance(args, dict):
            errors.append("工具参数必须是字典类型")
            return ValidationResult(valid=False, errors=errors, warnings=warnings)

        # JSON Schema 验证（简化版）
        if tool_schema:
            required = tool_schema.get("required", [])
            properties = tool_schema.get("properties", {})

            for field in required:
                if field not in args:
                    errors.append(f"缺少必填参数: {field}")

            for key, value in args.items():
                if key in properties:
                    expected_type = properties[key].get("type")
                    if expected_type and not self._check_type(value, expected_type):
                        errors.append(
                            f"参数 '{key}' 类型错误: 期望 {expected_type}, 实际 {type(value).__name__}"
                        )

        # 特定工具的安全检查
        if tool_name == "shell_exec":
            command = args.get("command", "")
            cmd_result = self.check_dangerous_command(command)
            if not cmd_result.valid:
                errors.extend(cmd_result.errors)

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def check_dangerous_command(self, command: str) -> ValidationResult:
        """检查命令是否包含危险操作."""
        errors: list[str] = []
        warnings: list[str] = []

        for pattern in DANGEROUS_COMMANDS:
            if re.search(pattern, command, re.IGNORECASE):
                errors.append(f"检测到危险命令: 匹配模式 '{pattern}'")

        # 检查 sudo 使用
        if re.search(r"\bsudo\b", command):
            warnings.append("使用了 sudo，请确认是否必要")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def check_sensitive_output(self, output: str) -> ValidationResult:
        """检查输出是否包含敏感信息."""
        warnings: list[str] = []

        for pattern in SENSITIVE_PATTERNS:
            matches = re.findall(pattern, output, re.IGNORECASE)
            if matches:
                warnings.append(f"输出可能包含敏感信息: {pattern}")

        return ValidationResult(
            valid=True,
            errors=[],
            warnings=warnings,
        )

    def validate_json_output(self, text: str) -> ValidationResult:
        """验证是否为有效 JSON."""
        errors: list[str] = []
        try:
            json.loads(text)
        except json.JSONDecodeError as e:
            errors.append(f"无效的 JSON 格式: {e}")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=[],
        )

    @staticmethod
    def _check_type(value, expected_type: str) -> bool:
        """简单类型检查."""
        type_map = {
            "string": str,
            "integer": int,
            "number": (int, float),
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        expected = type_map.get(expected_type)
        if expected is None:
            return True
        return isinstance(value, expected)
