"""符号提取器 / Symbol extractor.

从 AST 中提取代码符号（函数、类、方法、变量、接口）。
"""

import re
from dataclasses import dataclass, field

from app.services.deepwiki.parser import TreeNode


@dataclass
class CodeSymbol:
    """代码符号."""
    name: str
    kind: str           # function / class / method / variable / interface
    language: str
    file_path: str
    start_line: int
    end_line: int
    signature: str      # 函数签名 / 类声明
    docstring: str | None = None
    parent: str | None = None
    references: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "kind": self.kind,
            "language": self.language,
            "file_path": self.file_path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "signature": self.signature,
            "docstring": self.docstring,
            "parent": self.parent,
        }


class SymbolExtractor:
    """符号提取器.

    从解析后的 AST 中提取所有代码符号。
    支持多语言：Python / JavaScript / TypeScript / Java / Go。
    """

    def extract(
        self, tree: TreeNode, source: str, language: str, file_path: str = ""
    ) -> list[CodeSymbol]:
        """从 AST 提取所有符号."""
        if language == "python":
            return self._extract_python(tree, source, file_path)
        elif language in ("javascript", "typescript"):
            return self._extract_javascript(tree, source, file_path, language)
        elif language == "java":
            return self._extract_java(tree, source, file_path)
        elif language == "go":
            return self._extract_go(tree, source, file_path)
        else:
            return self._extract_generic(tree, source, file_path, language)

    def _extract_python(
        self, tree: TreeNode, source: str, file_path: str
    ) -> list[CodeSymbol]:
        """Python 符号提取."""
        symbols: list[CodeSymbol] = []
        lines = source.split("\n")

        for node in tree.children:
            if node.type == "class_definition":
                name = self._extract_name_from_text(
                    node.text, r"class\s+(\w+)"
                )
                if name:
                    docstring = self._extract_python_docstring(lines, node.start_line - 1)
                    sig = lines[node.start_line - 1].strip()
                    symbols.append(CodeSymbol(
                        name=name,
                        kind="class",
                        language="python",
                        file_path=file_path,
                        start_line=node.start_line,
                        end_line=node.end_line,
                        signature=sig,
                        docstring=docstring,
                    ))

                    # 提取方法
                    for child in node.children:
                        if child.type == "function_definition":
                            method_name = self._extract_name_from_text(
                                child.text, r"def\s+(\w+)"
                            )
                            if method_name:
                                method_doc = self._extract_python_docstring(
                                    lines, child.start_line - 1
                                )
                                method_sig = lines[child.start_line - 1].strip()
                                symbols.append(CodeSymbol(
                                    name=method_name,
                                    kind="method",
                                    language="python",
                                    file_path=file_path,
                                    start_line=child.start_line,
                                    end_line=child.end_line,
                                    signature=method_sig,
                                    docstring=method_doc,
                                    parent=name,
                                ))

            elif node.type == "function_definition":
                name = self._extract_name_from_text(
                    node.text, r"(?:async\s+)?def\s+(\w+)"
                )
                if name:
                    docstring = self._extract_python_docstring(lines, node.start_line - 1)
                    sig = lines[node.start_line - 1].strip()
                    symbols.append(CodeSymbol(
                        name=name,
                        kind="function",
                        language="python",
                        file_path=file_path,
                        start_line=node.start_line,
                        end_line=node.end_line,
                        signature=sig,
                        docstring=docstring,
                    ))

            elif node.type == "assignment":
                name = self._extract_name_from_text(
                    node.text, r"^(\w+)\s*="
                )
                if name and name.isupper():  # 只提取常量
                    symbols.append(CodeSymbol(
                        name=name,
                        kind="variable",
                        language="python",
                        file_path=file_path,
                        start_line=node.start_line,
                        end_line=node.end_line,
                        signature=lines[node.start_line - 1].strip(),
                    ))

        return symbols

    def _extract_javascript(
        self, tree: TreeNode, source: str, file_path: str, language: str
    ) -> list[CodeSymbol]:
        """JavaScript/TypeScript 符号提取."""
        symbols: list[CodeSymbol] = []
        lines = source.split("\n")

        for node in tree.children:
            first_line = lines[node.start_line - 1].strip() if node.start_line <= len(lines) else ""

            if node.type in ("class_declaration", "class_definition"):
                name = self._extract_name_from_text(first_line, r"class\s+(\w+)")
                if name:
                    symbols.append(CodeSymbol(
                        name=name,
                        kind="class",
                        language=language,
                        file_path=file_path,
                        start_line=node.start_line,
                        end_line=node.end_line,
                        signature=first_line,
                    ))

            elif node.type in ("function_declaration", "function_definition"):
                name = self._extract_name_from_text(first_line, r"function\s+(\w+)")
                if name:
                    symbols.append(CodeSymbol(
                        name=name,
                        kind="function",
                        language=language,
                        file_path=file_path,
                        start_line=node.start_line,
                        end_line=node.end_line,
                        signature=first_line,
                    ))

            elif node.type == "arrow_function":
                name = self._extract_name_from_text(first_line, r"(?:const|let|var)\s+(\w+)")
                if name:
                    symbols.append(CodeSymbol(
                        name=name,
                        kind="function",
                        language=language,
                        file_path=file_path,
                        start_line=node.start_line,
                        end_line=node.end_line,
                        signature=first_line,
                    ))

            elif node.type == "interface_declaration":
                name = self._extract_name_from_text(first_line, r"interface\s+(\w+)")
                if name:
                    symbols.append(CodeSymbol(
                        name=name,
                        kind="interface",
                        language=language,
                        file_path=file_path,
                        start_line=node.start_line,
                        end_line=node.end_line,
                        signature=first_line,
                    ))

            elif node.type == "type_alias":
                name = self._extract_name_from_text(first_line, r"type\s+(\w+)")
                if name:
                    symbols.append(CodeSymbol(
                        name=name,
                        kind="interface",
                        language=language,
                        file_path=file_path,
                        start_line=node.start_line,
                        end_line=node.end_line,
                        signature=first_line,
                    ))

        return symbols

    def _extract_java(
        self, tree: TreeNode, source: str, file_path: str
    ) -> list[CodeSymbol]:
        """Java 符号提取."""
        symbols: list[CodeSymbol] = []
        lines = source.split("\n")

        for node in tree.children:
            first_line = lines[node.start_line - 1].strip() if node.start_line <= len(lines) else ""

            if node.type == "class_declaration":
                name = self._extract_name_from_text(first_line, r"class\s+(\w+)")
                if name:
                    symbols.append(CodeSymbol(
                        name=name, kind="class", language="java",
                        file_path=file_path,
                        start_line=node.start_line, end_line=node.end_line,
                        signature=first_line,
                    ))

            elif node.type == "method_declaration":
                name = self._extract_name_from_text(first_line, r"(\w+)\s*\(")
                if name:
                    symbols.append(CodeSymbol(
                        name=name, kind="method", language="java",
                        file_path=file_path,
                        start_line=node.start_line, end_line=node.end_line,
                        signature=first_line,
                    ))

        return symbols

    def _extract_go(
        self, tree: TreeNode, source: str, file_path: str
    ) -> list[CodeSymbol]:
        """Go 符号提取."""
        symbols: list[CodeSymbol] = []
        lines = source.split("\n")

        for node in tree.children:
            first_line = lines[node.start_line - 1].strip() if node.start_line <= len(lines) else ""

            if node.type == "function_declaration":
                name = self._extract_name_from_text(first_line, r"func\s+(?:\(.*?\)\s+)?(\w+)")
                if name:
                    symbols.append(CodeSymbol(
                        name=name, kind="function", language="go",
                        file_path=file_path,
                        start_line=node.start_line, end_line=node.end_line,
                        signature=first_line,
                    ))

            elif node.type == "type_declaration":
                name = self._extract_name_from_text(first_line, r"type\s+(\w+)")
                if name:
                    symbols.append(CodeSymbol(
                        name=name, kind="class", language="go",
                        file_path=file_path,
                        start_line=node.start_line, end_line=node.end_line,
                        signature=first_line,
                    ))

        return symbols

    def _extract_generic(
        self, tree: TreeNode, source: str, file_path: str, language: str
    ) -> list[CodeSymbol]:
        """通用符号提取."""
        symbols: list[CodeSymbol] = []
        lines = source.split("\n")

        for node in tree.children:
            first_line = lines[node.start_line - 1].strip() if node.start_line <= len(lines) else ""
            name = self._extract_name_from_text(first_line, r"(?:class|struct|func|function|def)\s+(\w+)")
            if name:
                kind = "class" if "class" in first_line or "struct" in first_line else "function"
                symbols.append(CodeSymbol(
                    name=name, kind=kind, language=language,
                    file_path=file_path,
                    start_line=node.start_line, end_line=node.end_line,
                    signature=first_line,
                ))

        return symbols

    @staticmethod
    def _extract_name_from_text(text: str, pattern: str) -> str | None:
        """从文本中提取名称."""
        match = re.search(pattern, text)
        return match.group(1) if match else None

    @staticmethod
    def _extract_python_docstring(lines: list[str], start_idx: int) -> str | None:
        """提取 Python docstring."""
        for i in range(start_idx + 1, min(start_idx + 5, len(lines))):
            stripped = lines[i].strip()
            if stripped.startswith('"""') or stripped.startswith("'''"):
                quote = stripped[:3]
                if stripped.endswith(quote) and len(stripped) > 6:
                    return stripped[3:-3]
                # 多行 docstring
                doc_lines = [stripped[3:]]
                for j in range(i + 1, min(i + 20, len(lines))):
                    if lines[j].strip().endswith(quote):
                        doc_lines.append(lines[j].strip()[:-3])
                        return "\n".join(doc_lines).strip()
                    doc_lines.append(lines[j].strip())
                return "\n".join(doc_lines).strip()
            elif stripped and not stripped.startswith("#"):
                break
        return None
