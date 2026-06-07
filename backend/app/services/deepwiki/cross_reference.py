"""符号交叉引用 / Cross-reference analysis.

分析符号之间的引用关系：
- 谁定义了这个符号
- 谁引用/调用了这个符号
- 符号的导出/导入关系
"""

import re
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Reference:
    """引用记录."""

    symbol_name: str
    file_path: str
    line: int
    ref_type: str  # "definition" / "usage" / "import"
    context: str = ""  # 所在行文本

    def to_dict(self) -> dict:
        return {
            "symbol_name": self.symbol_name,
            "file_path": self.file_path,
            "line": self.line,
            "ref_type": self.ref_type,
            "context": self.context[:200],
        }


@dataclass
class SymbolRefs:
    """符号的所有引用."""

    name: str
    definition: Reference | None = None
    usages: list[Reference] = field(default_factory=list)
    imports: list[Reference] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "definition": self.definition.to_dict() if self.definition else None,
            "usage_count": len(self.usages),
            "import_count": len(self.imports),
            "usages": [u.to_dict() for u in self.usages[:20]],
            "imports": [i.to_dict() for i in self.imports[:20]],
        }


# 定义模式
_DEF_PATTERNS = {
    "python": re.compile(
        r"^(?:async\s+)?(?:def|class)\s+(\w+)", re.MULTILINE
    ),
    "javascript": re.compile(
        r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=|class\s+(\w+))",
        re.MULTILINE,
    ),
    "typescript": re.compile(
        r"(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*(?::\s*\w+)?\s*=|class\s+(\w+)|interface\s+(\w+)|type\s+(\w+))",
        re.MULTILINE,
    ),
}

# 导入模式
_IMPORT_PATTERNS = {
    "python": re.compile(
        r"(?:from\s+\S+\s+import\s+(.+)|import\s+(.+))", re.MULTILINE
    ),
    "javascript": re.compile(
        r"(?:import\s+(?:{([^}]+)}|(\w+))\s+from|require\(['\"]([^'\"]+)['\"]\))",
        re.MULTILINE,
    ),
    "typescript": re.compile(
        r"import\s+(?:{([^}]+)}|(\w+))\s+from",
        re.MULTILINE,
    ),
}

_EXT_TO_LANG = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
}


class CrossReferenceAnalyzer:
    """交叉引用分析器."""

    def __init__(self):
        self._definitions: dict[str, Reference] = {}
        self._all_refs: dict[str, SymbolRefs] = {}

    def analyze(self, root_path: str) -> dict:
        """分析项目中的交叉引用.

        Returns:
            {symbols: [...], stats: {...}}
        """
        root = Path(root_path)
        if not root.exists():
            return {"symbols": [], "stats": {}}

        ignore_dirs = {
            ".git", "node_modules", "__pycache__", ".venv",
            "dist", "build", ".next",
        }

        files_data: list[tuple[str, str, str]] = []  # (rel_path, lang, code)

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

            rel_path = str(fpath.relative_to(root))
            files_data.append((rel_path, lang, code))

        # Pass 1: 收集所有定义
        for rel_path, lang, code in files_data:
            self._collect_definitions(rel_path, lang, code)

        # Pass 2: 查找所有引用
        for rel_path, lang, code in files_data:
            self._collect_usages(rel_path, lang, code)

        # 统计
        symbols = sorted(
            self._all_refs.values(),
            key=lambda s: len(s.usages),
            reverse=True,
        )

        unused = [
            s.name for s in symbols
            if len(s.usages) == 0 and not s.name.startswith("_")
        ]

        return {
            "symbols": [s.to_dict() for s in symbols[:100]],
            "stats": {
                "total_symbols": len(self._all_refs),
                "total_usages": sum(len(s.usages) for s in symbols),
                "most_referenced": [
                    {"name": s.name, "count": len(s.usages)}
                    for s in symbols[:10]
                ],
                "potentially_unused": unused[:20],
            },
        }

    def _collect_definitions(
        self, rel_path: str, lang: str, code: str
    ) -> None:
        """收集定义."""
        pattern = _DEF_PATTERNS.get(lang)
        if not pattern:
            return

        lines = code.split("\n")

        for match in pattern.finditer(code):
            name = None
            for g in range(1, match.lastindex + 1 if match.lastindex else 1):
                if match.group(g):
                    name = match.group(g).strip()
                    break

            if not name:
                continue

            line_num = code[:match.start()].count("\n") + 1
            context = lines[line_num - 1] if line_num <= len(lines) else ""

            ref = Reference(
                symbol_name=name,
                file_path=rel_path,
                line=line_num,
                ref_type="definition",
                context=context.strip(),
            )
            self._definitions[name] = ref

            if name not in self._all_refs:
                self._all_refs[name] = SymbolRefs(name=name)
            self._all_refs[name].definition = ref

    def _collect_usages(
        self, rel_path: str, lang: str, code: str
    ) -> None:
        """收集使用引用."""
        lines = code.split("\n")

        for name in self._definitions:
            if len(name) < 2:
                continue

            pattern = re.compile(r"\b" + re.escape(name) + r"\b")
            for i, line in enumerate(lines, 1):
                for match in pattern.finditer(line):
                    # 跳过定义本身
                    def_ref = self._definitions.get(name)
                    if (
                        def_ref
                        and def_ref.file_path == rel_path
                        and def_ref.line == i
                    ):
                        continue

                    # 检测是否为 import
                    is_import = any(
                        kw in line
                        for kw in ("import ", "from ", "require(")
                    )

                    ref = Reference(
                        symbol_name=name,
                        file_path=rel_path,
                        line=i,
                        ref_type="import" if is_import else "usage",
                        context=line.strip(),
                    )

                    if name not in self._all_refs:
                        self._all_refs[name] = SymbolRefs(name=name)

                    if is_import:
                        self._all_refs[name].imports.append(ref)
                    else:
                        self._all_refs[name].usages.append(ref)
