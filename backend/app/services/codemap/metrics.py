"""代码度量 / Code metrics.

计算代码质量指标：
- 圈复杂度 (Cyclomatic Complexity)
- 代码行数统计 (LOC/SLOC/Comments)
- 函数长度分布
- 文件复杂度热力图数据
"""

import re
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class FileMetrics:
    """文件级度量."""

    path: str
    language: str
    total_lines: int = 0
    code_lines: int = 0
    comment_lines: int = 0
    blank_lines: int = 0
    functions: int = 0
    classes: int = 0
    max_function_length: int = 0
    avg_function_length: float = 0
    complexity: int = 0  # 圈复杂度

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "language": self.language,
            "total_lines": self.total_lines,
            "code_lines": self.code_lines,
            "comment_lines": self.comment_lines,
            "blank_lines": self.blank_lines,
            "functions": self.functions,
            "classes": self.classes,
            "max_function_length": self.max_function_length,
            "avg_function_length": round(self.avg_function_length, 1),
            "complexity": self.complexity,
            "comment_ratio": (
                round(self.comment_lines / max(self.code_lines, 1) * 100, 1)
            ),
        }


@dataclass
class ProjectMetrics:
    """项目级度量."""

    files: list[FileMetrics] = field(default_factory=list)

    def to_dict(self) -> dict:
        total_lines = sum(f.total_lines for f in self.files)
        total_code = sum(f.code_lines for f in self.files)
        total_comments = sum(f.comment_lines for f in self.files)
        total_blank = sum(f.blank_lines for f in self.files)
        total_functions = sum(f.functions for f in self.files)
        total_classes = sum(f.classes for f in self.files)

        by_language: dict[str, dict] = {}
        for f in self.files:
            lang = f.language
            if lang not in by_language:
                by_language[lang] = {
                    "files": 0, "lines": 0, "code_lines": 0,
                }
            by_language[lang]["files"] += 1
            by_language[lang]["lines"] += f.total_lines
            by_language[lang]["code_lines"] += f.code_lines

        # 复杂度热力图
        heatmap = sorted(
            [{"path": f.path, "complexity": f.complexity} for f in self.files],
            key=lambda x: x["complexity"],
            reverse=True,
        )[:20]

        # 最长函数
        longest_funcs = sorted(
            [
                {"path": f.path, "max_function_length": f.max_function_length}
                for f in self.files
                if f.max_function_length > 0
            ],
            key=lambda x: x["max_function_length"],
            reverse=True,
        )[:10]

        return {
            "summary": {
                "total_files": len(self.files),
                "total_lines": total_lines,
                "code_lines": total_code,
                "comment_lines": total_comments,
                "blank_lines": total_blank,
                "total_functions": total_functions,
                "total_classes": total_classes,
                "comment_ratio": round(
                    total_comments / max(total_code, 1) * 100, 1
                ),
            },
            "by_language": by_language,
            "complexity_heatmap": heatmap,
            "longest_functions": longest_funcs,
            "files": [f.to_dict() for f in self.files],
        }


# 复杂度计算关键字
_COMPLEXITY_KEYWORDS = {
    "python": ["if ", "elif ", "for ", "while ", "except ", "and ", "or "],
    "javascript": ["if ", "else if", "for ", "while ", "catch ", "&&", "||", "?"],
    "typescript": ["if ", "else if", "for ", "while ", "catch ", "&&", "||", "?"],
    "java": ["if ", "else if", "for ", "while ", "catch ", "&&", "||", "?"],
    "go": ["if ", "for ", "case ", "&&", "||"],
}

# 注释模式
_COMMENT_PATTERNS = {
    "python": (re.compile(r"^\s*#"), re.compile(r'"""'), re.compile(r"'''")),
    "javascript": (re.compile(r"^\s*//"), re.compile(r"/\*"), re.compile(r"\*/")),
    "typescript": (re.compile(r"^\s*//"), re.compile(r"/\*"), re.compile(r"\*/")),
    "java": (re.compile(r"^\s*//"), re.compile(r"/\*"), re.compile(r"\*/")),
    "go": (re.compile(r"^\s*//"), re.compile(r"/\*"), re.compile(r"\*/")),
}

_EXT_TO_LANG = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".c": "c",
    ".cpp": "cpp",
    ".rb": "ruby",
    ".php": "php",
}


class MetricsAnalyzer:
    """代码度量分析器."""

    def analyze(self, root_path: str) -> dict:
        """分析项目代码度量.

        Args:
            root_path: 项目根目录

        Returns:
            ProjectMetrics 字典
        """
        root = Path(root_path)
        if not root.exists():
            return ProjectMetrics().to_dict()

        project = ProjectMetrics()
        ignore_dirs = {
            ".git", "node_modules", "__pycache__", ".venv",
            "dist", "build", "vendor", ".next",
        }

        for fpath in root.rglob("*"):
            if any(p in fpath.parts for p in ignore_dirs):
                continue
            if not fpath.is_file():
                continue

            ext = fpath.suffix.lower()
            lang = _EXT_TO_LANG.get(ext)
            if not lang:
                continue

            try:
                code = fpath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            metrics = self._analyze_file(
                str(fpath.relative_to(root)), lang, code
            )
            project.files.append(metrics)

        return project.to_dict()

    def _analyze_file(self, path: str, language: str, code: str) -> FileMetrics:
        """分析单个文件."""
        lines = code.split("\n")
        metrics = FileMetrics(path=path, language=language)
        metrics.total_lines = len(lines)

        # 行分类
        in_block_comment = False
        func_lengths: list[int] = []
        current_func_start: int | None = None

        for i, line in enumerate(lines):
            stripped = line.strip()

            if not stripped:
                metrics.blank_lines += 1
                continue

            # 注释检测（简化版）
            if language == "python":
                if stripped.startswith("#"):
                    metrics.comment_lines += 1
                    continue
                if '"""' in stripped or "'''" in stripped:
                    in_block_comment = not in_block_comment
                    metrics.comment_lines += 1
                    continue
            else:
                if stripped.startswith("//"):
                    metrics.comment_lines += 1
                    continue
                if "/*" in stripped:
                    in_block_comment = True
                    metrics.comment_lines += 1
                    if "*/" in stripped:
                        in_block_comment = False
                    continue
                if "*/" in stripped:
                    in_block_comment = False
                    metrics.comment_lines += 1
                    continue

            if in_block_comment:
                metrics.comment_lines += 1
                continue

            metrics.code_lines += 1

            # 函数/类统计
            if language == "python":
                if re.match(r"^(async\s+)?def\s+\w+", stripped):
                    metrics.functions += 1
                    if current_func_start is not None:
                        func_lengths.append(i - current_func_start)
                    current_func_start = i
                elif stripped.startswith("class "):
                    metrics.classes += 1
            elif language in ("javascript", "typescript"):
                if re.match(
                    r"(function\s+\w+|(?:const|let|var)\s+\w+\s*=\s*(?:async\s+)?(?:function|\())",
                    stripped,
                ):
                    metrics.functions += 1
                    if current_func_start is not None:
                        func_lengths.append(i - current_func_start)
                    current_func_start = i
                elif re.match(r"class\s+\w+", stripped):
                    metrics.classes += 1

        # 最后一个函数
        if current_func_start is not None:
            func_lengths.append(len(lines) - current_func_start)

        if func_lengths:
            metrics.max_function_length = max(func_lengths)
            metrics.avg_function_length = sum(func_lengths) / len(func_lengths)

        # 圈复杂度（基线为1，每个分支+1）
        keywords = _COMPLEXITY_KEYWORDS.get(language, [])
        metrics.complexity = 1
        for line in lines:
            for kw in keywords:
                metrics.complexity += line.count(kw)

        return metrics
