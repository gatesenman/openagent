"""函数调用图 / Call graph.

静态分析函数间的调用关系，生成调用图。
用于:
- 影响分析（修改一个函数会影响哪些调用者）
- 死代码检测（没有被调用的函数）
- 热路径分析（被最多函数调用的核心函数）
"""

import re
import logging
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class CallEdge:
    """调用边."""

    caller: str       # 调用者 (file:function)
    callee: str       # 被调用者 (函数名)
    call_type: str = "direct"  # direct / indirect / dynamic
    line: int = 0

    def to_dict(self) -> dict:
        return {
            "caller": self.caller,
            "callee": self.callee,
            "call_type": self.call_type,
            "line": self.line,
        }


@dataclass
class FunctionNode:
    """函数节点."""

    name: str
    file_path: str
    start_line: int
    end_line: int
    calls: list[str] = field(default_factory=list)     # 调用了哪些函数
    called_by: list[str] = field(default_factory=list)  # 被哪些函数调用

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "calls_count": len(self.calls),
            "called_by_count": len(self.called_by),
            "calls": self.calls[:20],
            "called_by": self.called_by[:20],
        }


# 函数定义正则模式
_FUNC_PATTERNS = {
    "python": re.compile(
        r"^(?:async\s+)?def\s+(\w+)\s*\(", re.MULTILINE
    ),
    "javascript": re.compile(
        r"(?:function\s+(\w+)\s*\(|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\())",
        re.MULTILINE,
    ),
    "typescript": re.compile(
        r"(?:function\s+(\w+)\s*[\(<]|(?:const|let|var)\s+(\w+)\s*(?::\s*\w+)?\s*=\s*(?:async\s+)?(?:function|\())",
        re.MULTILINE,
    ),
    "java": re.compile(
        r"(?:public|private|protected|static|\s)+\w+(?:<[\w,\s]+>)?\s+(\w+)\s*\(",
        re.MULTILINE,
    ),
    "go": re.compile(r"^func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\(", re.MULTILINE),
}

# 函数调用正则模式（简化：识别 name(... 模式）
_CALL_PATTERN = re.compile(r"\b(\w+)\s*\(")

# 排除的内置函数/关键字
_BUILTIN_EXCLUDES = {
    "if", "for", "while", "return", "print", "len", "range", "str", "int",
    "float", "bool", "list", "dict", "set", "tuple", "type", "isinstance",
    "super", "self", "cls", "None", "True", "False", "import", "from",
    "class", "def", "async", "await", "try", "except", "finally", "with",
    "raise", "yield", "assert", "pass", "break", "continue", "del",
    "new", "var", "let", "const", "function", "catch", "throw",
    "switch", "case", "default", "void", "null", "undefined",
    "console", "require", "module", "exports",
}

# 语言扩展名映射
_EXT_TO_LANG = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
}


class CallGraph:
    """函数调用图生成器."""

    def __init__(self):
        self._functions: dict[str, FunctionNode] = {}
        self._edges: list[CallEdge] = []

    def build(self, root_path: str) -> dict:
        """构建调用图.

        Args:
            root_path: 项目根目录

        Returns:
            {functions: [...], edges: [...], stats: {...}}
        """
        root = Path(root_path)
        if not root.exists():
            return {"functions": [], "edges": [], "stats": {}}

        # 1. 扫描所有函数定义
        self._scan_definitions(root)

        # 2. 分析函数调用关系
        self._analyze_calls(root)

        # 3. 统计
        all_func_names = set(self._functions.keys())
        called_funcs = set()
        for edge in self._edges:
            called_funcs.add(edge.callee)

        uncalled = all_func_names - called_funcs
        # 排除 main/init 等入口函数
        uncalled = {
            f for f in uncalled
            if not any(
                k in f.lower()
                for k in ("main", "__init__", "test_", "setup", "teardown")
            )
        }

        return {
            "functions": [f.to_dict() for f in self._functions.values()],
            "edges": [e.to_dict() for e in self._edges],
            "stats": {
                "total_functions": len(self._functions),
                "total_edges": len(self._edges),
                "potentially_unused": sorted(uncalled)[:50],
                "most_called": self._top_called(10),
                "most_calling": self._top_calling(10),
            },
        }

    def _scan_definitions(self, root: Path) -> None:
        """扫描所有函数定义."""
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

            pattern = _FUNC_PATTERNS.get(lang)
            if not pattern:
                continue

            rel_path = str(fpath.relative_to(root))
            lines = code.split("\n")

            for match in pattern.finditer(code):
                name = match.group(1) or (
                    match.group(2) if match.lastindex and match.lastindex >= 2 else None
                )
                if not name or name in _BUILTIN_EXCLUDES:
                    continue

                start_line = code[:match.start()].count("\n") + 1
                end_line = min(start_line + 50, len(lines))

                key = f"{rel_path}:{name}"
                self._functions[key] = FunctionNode(
                    name=name,
                    file_path=rel_path,
                    start_line=start_line,
                    end_line=end_line,
                )

    def _analyze_calls(self, root: Path) -> None:
        """分析调用关系."""
        known_names = {
            fn.name for fn in self._functions.values()
        }

        for key, func_node in self._functions.items():
            fpath = root / func_node.file_path
            try:
                code = fpath.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            lines = code.split("\n")
            func_body = "\n".join(
                lines[func_node.start_line - 1 : func_node.end_line]
            )

            for match in _CALL_PATTERN.finditer(func_body):
                callee = match.group(1)
                if callee in _BUILTIN_EXCLUDES:
                    continue
                if callee == func_node.name:
                    continue  # 递归调用不计
                if callee not in known_names:
                    continue

                line = func_node.start_line + func_body[:match.start()].count("\n")
                edge = CallEdge(
                    caller=key,
                    callee=callee,
                    line=line,
                )
                self._edges.append(edge)
                func_node.calls.append(callee)

                # 更新被调用方
                for other_key, other_node in self._functions.items():
                    if other_node.name == callee:
                        other_node.called_by.append(key)
                        break

    def _top_called(self, n: int) -> list[dict]:
        """被调用次数最多的函数."""
        counts: dict[str, int] = {}
        for edge in self._edges:
            counts[edge.callee] = counts.get(edge.callee, 0) + 1
        sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [{"name": k, "count": v} for k, v in sorted_items[:n]]

    def _top_calling(self, n: int) -> list[dict]:
        """调用其他函数最多的函数."""
        counts: dict[str, int] = {}
        for edge in self._edges:
            counts[edge.caller] = counts.get(edge.caller, 0) + 1
        sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return [{"name": k, "count": v} for k, v in sorted_items[:n]]
