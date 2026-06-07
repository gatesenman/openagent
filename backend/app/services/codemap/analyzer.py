"""代码结构分析器 / Code structure analyzer.

分析项目的模块结构、导入关系和复杂度。
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path

from app.services.deepwiki.parser import CodeParser, LANGUAGE_MAP

IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".next", "dist", "build", ".cache", "target", "vendor",
}


@dataclass
class ModuleInfo:
    """模块信息."""
    path: str
    name: str
    language: str
    symbols: list[str] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    size_lines: int = 0
    complexity: int = 0

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "name": self.name,
            "language": self.language,
            "symbols": self.symbols,
            "imports": self.imports,
            "size_lines": self.size_lines,
            "complexity": self.complexity,
        }


class CodeAnalyzer:
    """代码结构分析器.

    分析项目中每个代码模块的：
    - 导出符号
    - 导入依赖
    - 代码行数
    - 圈复杂度
    """

    def __init__(self):
        self.parser = CodeParser()

    def analyze_directory(self, dir_path: str) -> list[ModuleInfo]:
        """分析目录中所有代码模块."""
        modules: list[ModuleInfo] = []
        root = Path(dir_path)

        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

            for filename in filenames:
                file_path = Path(dirpath) / filename
                language = self.parser.get_language_for_file(filename)
                if language:
                    module = self.analyze_file(str(file_path), str(root))
                    if module:
                        modules.append(module)

        return modules

    def analyze_file(self, file_path: str, root_path: str = "") -> ModuleInfo | None:
        """分析单个文件."""
        language = self.parser.get_language_for_file(file_path)
        if not language:
            return None

        try:
            content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return None

        lines = content.split("\n")
        rel_path = os.path.relpath(file_path, root_path) if root_path else file_path

        imports = self._extract_imports(content, language)
        symbols = self._extract_export_names(content, language)
        complexity = self._calculate_complexity(content, language)

        return ModuleInfo(
            path=rel_path,
            name=Path(file_path).stem,
            language=language,
            symbols=symbols,
            imports=imports,
            size_lines=len(lines),
            complexity=complexity,
        )

    def _extract_imports(self, code: str, language: str) -> list[str]:
        """提取导入语句."""
        imports: list[str] = []

        if language == "python":
            for match in re.finditer(r"^(?:from\s+(\S+)\s+)?import\s+(.+)$", code, re.MULTILINE):
                module = match.group(1) or match.group(2).split(",")[0].strip().split(" as ")[0]
                imports.append(module)

        elif language in ("javascript", "typescript"):
            for match in re.finditer(r"(?:import|require)\s*\(?['\"]([^'\"]+)['\"]", code):
                imports.append(match.group(1))

        elif language == "java":
            for match in re.finditer(r"^import\s+([\w.]+);", code, re.MULTILINE):
                imports.append(match.group(1))

        elif language == "go":
            for match in re.finditer(r'"([^"]+)"', code):
                imports.append(match.group(1))

        return imports

    def _extract_export_names(self, code: str, language: str) -> list[str]:
        """提取导出/定义的符号名."""
        names: list[str] = []

        if language == "python":
            for match in re.finditer(r"^(?:class|def|async\s+def)\s+(\w+)", code, re.MULTILINE):
                names.append(match.group(1))

        elif language in ("javascript", "typescript"):
            for match in re.finditer(r"(?:export\s+)?(?:default\s+)?(?:class|function|const|let|var|interface|type)\s+(\w+)", code, re.MULTILINE):
                names.append(match.group(1))

        elif language == "java":
            for match in re.finditer(r"(?:public|private|protected)?\s*(?:static\s+)?(?:class|interface|enum)\s+(\w+)", code, re.MULTILINE):
                names.append(match.group(1))

        elif language == "go":
            for match in re.finditer(r"(?:func|type)\s+(\w+)", code, re.MULTILINE):
                names.append(match.group(1))

        return names

    def _calculate_complexity(self, code: str, language: str) -> int:
        """计算圈复杂度（简化版）.

        复杂度 = 1（基础） + 分支/循环/异常关键词数量
        """
        complexity = 1

        branch_keywords = {
            "python": [r"\bif\b", r"\belif\b", r"\bfor\b", r"\bwhile\b", r"\bexcept\b", r"\band\b", r"\bor\b"],
            "javascript": [r"\bif\b", r"\belse\s+if\b", r"\bfor\b", r"\bwhile\b", r"\bcatch\b", r"\bcase\b", r"\b&&\b", r"\b\|\|\b"],
            "typescript": [r"\bif\b", r"\belse\s+if\b", r"\bfor\b", r"\bwhile\b", r"\bcatch\b", r"\bcase\b", r"\b&&\b", r"\b\|\|\b"],
            "java": [r"\bif\b", r"\belse\s+if\b", r"\bfor\b", r"\bwhile\b", r"\bcatch\b", r"\bcase\b", r"&&", r"\|\|"],
            "go": [r"\bif\b", r"\bfor\b", r"\bcase\b", r"&&", r"\|\|"],
        }

        patterns = branch_keywords.get(language, branch_keywords.get("python", []))
        for pattern in patterns:
            complexity += len(re.findall(pattern, code))

        return complexity
