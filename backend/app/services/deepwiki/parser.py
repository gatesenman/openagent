"""代码解析器 / Code parser.

使用 tree-sitter 解析源代码为 AST。
如果 tree-sitter 不可用，降级为正则解析。
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# tree-sitter 可选依赖
try:
    import tree_sitter
    _TS_AVAILABLE = True
except ImportError:
    _TS_AVAILABLE = False
    logger.warning("tree-sitter 未安装，使用正则解析器")

# 语言扩展名映射
LANGUAGE_MAP: dict[str, str] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".rs": "rust",
    ".c": "c",
    ".h": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".hpp": "cpp",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
}


@dataclass
class TreeNode:
    """AST 节点."""
    type: str
    text: str
    start_line: int
    end_line: int
    start_col: int = 0
    end_col: int = 0
    children: list["TreeNode"] = field(default_factory=list)


class CodeParser:
    """多语言代码解析器.

    优先使用 tree-sitter 进行精确的 AST 解析。
    如果不可用，降级为基于正则的简单解析。
    """

    SUPPORTED_LANGUAGES = list(set(LANGUAGE_MAP.values()))

    def __init__(self):
        self._ts_parsers: dict[str, Any] = {}

    def get_language_for_file(self, filename: str) -> str | None:
        """根据文件扩展名判断语言."""
        ext = Path(filename).suffix.lower()
        return LANGUAGE_MAP.get(ext)

    def parse(self, code: str, language: str) -> TreeNode:
        """解析代码为 AST."""
        if _TS_AVAILABLE:
            try:
                return self._parse_with_treesitter(code, language)
            except Exception as e:
                logger.warning("tree-sitter 解析失败，降级为正则: %s", e)

        return self._parse_with_regex(code, language)

    def _parse_with_treesitter(self, code: str, language: str) -> TreeNode:
        """使用 tree-sitter 解析."""
        parser = tree_sitter.Parser()
        # 加载语言（需要已安装对应的 tree-sitter-{language} 包）
        try:
            lang = tree_sitter.Language(f"tree-sitter-{language}")
            parser.language = lang
        except Exception:
            raise RuntimeError(f"tree-sitter language not available: {language}")

        tree = parser.parse(bytes(code, "utf-8"))
        return self._convert_ts_node(tree.root_node, code)

    def _convert_ts_node(self, node: Any, source: str) -> TreeNode:
        """转换 tree-sitter 节点为内部 TreeNode."""
        children = []
        for child in node.children:
            children.append(self._convert_ts_node(child, source))

        return TreeNode(
            type=node.type,
            text=source[node.start_byte:node.end_byte],
            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,
            start_col=node.start_point[1],
            end_col=node.end_point[1],
            children=children,
        )

    def _parse_with_regex(self, code: str, language: str) -> TreeNode:
        """使用正则表达式解析（降级方案）."""
        lines = code.split("\n")
        root = TreeNode(
            type="module",
            text=code,
            start_line=1,
            end_line=len(lines),
        )

        if language == "python":
            root.children = self._parse_python_regex(code)
        elif language in ("javascript", "typescript"):
            root.children = self._parse_js_regex(code)
        elif language == "java":
            root.children = self._parse_java_regex(code)
        elif language == "go":
            root.children = self._parse_go_regex(code)
        else:
            root.children = self._parse_generic_regex(code)

        return root

    def _parse_python_regex(self, code: str) -> list[TreeNode]:
        """Python 正则解析."""
        nodes: list[TreeNode] = []
        lines = code.split("\n")

        patterns = [
            (r"^(class)\s+(\w+)", "class_definition"),
            (r"^(\s*def)\s+(\w+)", "function_definition"),
            (r"^(\s*async\s+def)\s+(\w+)", "function_definition"),
            (r"^(\w+)\s*=", "assignment"),
        ]

        for i, line in enumerate(lines, 1):
            for pattern, node_type in patterns:
                match = re.match(pattern, line)
                if match:
                    # 找到块的结束行
                    end = self._find_block_end_python(lines, i - 1)
                    text = "\n".join(lines[i - 1:end])
                    nodes.append(TreeNode(
                        type=node_type,
                        text=text,
                        start_line=i,
                        end_line=end,
                    ))
                    break

        return nodes

    def _parse_js_regex(self, code: str) -> list[TreeNode]:
        """JavaScript/TypeScript 正则解析."""
        nodes: list[TreeNode] = []
        lines = code.split("\n")

        patterns = [
            (r"(?:export\s+)?(?:default\s+)?class\s+(\w+)", "class_declaration"),
            (r"(?:export\s+)?(?:async\s+)?function\s+(\w+)", "function_declaration"),
            (r"(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(", "arrow_function"),
            (r"(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=", "variable_declaration"),
            (r"(?:export\s+)?interface\s+(\w+)", "interface_declaration"),
            (r"(?:export\s+)?type\s+(\w+)", "type_alias"),
        ]

        for i, line in enumerate(lines, 1):
            for pattern, node_type in patterns:
                match = re.search(pattern, line)
                if match:
                    end = self._find_block_end_braces(lines, i - 1)
                    text = "\n".join(lines[i - 1:end])
                    nodes.append(TreeNode(
                        type=node_type,
                        text=text,
                        start_line=i,
                        end_line=end,
                    ))
                    break

        return nodes

    def _parse_java_regex(self, code: str) -> list[TreeNode]:
        """Java 正则解析."""
        nodes: list[TreeNode] = []
        lines = code.split("\n")

        for i, line in enumerate(lines, 1):
            if re.search(r"(?:public|private|protected)?\s*(?:static\s+)?class\s+\w+", line):
                end = self._find_block_end_braces(lines, i - 1)
                nodes.append(TreeNode(type="class_declaration", text="\n".join(lines[i-1:end]), start_line=i, end_line=end))
            elif re.search(r"(?:public|private|protected)?\s*(?:static\s+)?\w+\s+\w+\s*\(", line):
                end = self._find_block_end_braces(lines, i - 1)
                nodes.append(TreeNode(type="method_declaration", text="\n".join(lines[i-1:end]), start_line=i, end_line=end))

        return nodes

    def _parse_go_regex(self, code: str) -> list[TreeNode]:
        """Go 正则解析."""
        nodes: list[TreeNode] = []
        lines = code.split("\n")

        for i, line in enumerate(lines, 1):
            if re.match(r"func\s+", line):
                end = self._find_block_end_braces(lines, i - 1)
                nodes.append(TreeNode(type="function_declaration", text="\n".join(lines[i-1:end]), start_line=i, end_line=end))
            elif re.match(r"type\s+\w+\s+struct", line):
                end = self._find_block_end_braces(lines, i - 1)
                nodes.append(TreeNode(type="type_declaration", text="\n".join(lines[i-1:end]), start_line=i, end_line=end))

        return nodes

    def _parse_generic_regex(self, code: str) -> list[TreeNode]:
        """通用正则解析."""
        nodes: list[TreeNode] = []
        lines = code.split("\n")

        for i, line in enumerate(lines, 1):
            if re.match(r"\s*(class|struct|enum|interface)\s+\w+", line):
                end = self._find_block_end_braces(lines, i - 1)
                nodes.append(TreeNode(type="type_definition", text="\n".join(lines[i-1:end]), start_line=i, end_line=end))
            elif re.search(r"\w+\s+\w+\s*\(", line) and "{" in line:
                end = self._find_block_end_braces(lines, i - 1)
                nodes.append(TreeNode(type="function_definition", text="\n".join(lines[i-1:end]), start_line=i, end_line=end))

        return nodes

    @staticmethod
    def _find_block_end_python(lines: list[str], start: int) -> int:
        """找到 Python 代码块结束行（基于缩进）."""
        if start >= len(lines):
            return start + 1

        base_indent = len(lines[start]) - len(lines[start].lstrip())

        for i in range(start + 1, len(lines)):
            line = lines[i]
            if line.strip() == "":
                continue
            indent = len(line) - len(line.lstrip())
            if indent <= base_indent and line.strip():
                return i
        return len(lines)

    @staticmethod
    def _find_block_end_braces(lines: list[str], start: int) -> int:
        """找到花括号代码块结束行."""
        depth = 0
        found_open = False

        for i in range(start, len(lines)):
            for ch in lines[i]:
                if ch == "{":
                    depth += 1
                    found_open = True
                elif ch == "}":
                    depth -= 1
                    if found_open and depth == 0:
                        return i + 1

        return len(lines)
