"""仓库索引器 / Repository indexer.

遍历仓库文件，解析 → 提取符号 → 生成 embedding → 索引。
支持增量索引。
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from app.services.deepwiki.doc_generator import DocGenerator
from app.services.deepwiki.embedding_service import embedding_service
from app.services.deepwiki.parser import CodeParser
from app.services.deepwiki.symbol_extractor import CodeSymbol, SymbolExtractor

logger = logging.getLogger(__name__)

# 忽略的目录和文件
IGNORE_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv",
    ".next", "dist", "build", ".cache", ".tox", "target",
    "vendor", ".idea", ".vscode", "coverage", ".pytest_cache",
}

IGNORE_FILES = {
    ".gitignore", ".dockerignore", "package-lock.json",
    "yarn.lock", "pnpm-lock.yaml", "Pipfile.lock",
    "poetry.lock", "go.sum",
}

MAX_FILE_SIZE = 500_000  # 500KB


@dataclass
class IndexResult:
    """索引结果."""
    total_files: int = 0
    indexed_files: int = 0
    total_symbols: int = 0
    errors: list[str] = field(default_factory=list)
    languages: dict[str, int] = field(default_factory=dict)


class RepoIndexer:
    """仓库索引器.

    完整的代码索引管道：
    1. 遍历所有代码文件
    2. 解析每个文件的 AST（tree-sitter / regex）
    3. 提取符号（函数/类/方法/接口）
    4. 生成 embedding 用于语义搜索
    5. 可选：生成符号文档
    """

    def __init__(self):
        self.parser = CodeParser()
        self.extractor = SymbolExtractor()
        self.doc_generator = DocGenerator()
        self._indexed_symbols: dict[str, list[CodeSymbol]] = {}

    async def index_repo(self, repo_path: str) -> IndexResult:
        """索引整个仓库."""
        result = IndexResult()
        all_symbols: list[CodeSymbol] = []

        root = Path(repo_path)
        if not root.exists():
            result.errors.append(f"路径不存在: {repo_path}")
            return result

        for file_path in self._walk_code_files(root):
            result.total_files += 1

            try:
                symbols = await self.index_file(str(file_path))
                if symbols:
                    result.indexed_files += 1
                    result.total_symbols += len(symbols)
                    all_symbols.extend(symbols)

                    # 统计语言
                    lang = symbols[0].language if symbols else "unknown"
                    result.languages[lang] = result.languages.get(lang, 0) + 1
            except Exception as e:
                result.errors.append(f"{file_path}: {e}")

        # 生成 embedding 索引
        if all_symbols:
            texts = [
                f"{s.name} {s.kind} {s.signature} {s.docstring or ''}"
                for s in all_symbols
            ]
            metadata = [
                {
                    "file_path": s.file_path,
                    "symbol_name": s.name,
                    "content": s.signature,
                }
                for s in all_symbols
            ]
            try:
                await embedding_service.index(texts, metadata)
            except Exception as e:
                result.errors.append(f"Embedding 索引失败: {e}")

        self._indexed_symbols[repo_path] = all_symbols
        logger.info(
            "仓库索引完成: %s, 文件=%d, 符号=%d",
            repo_path, result.indexed_files, result.total_symbols,
        )
        return result

    async def index_file(self, file_path: str) -> list[CodeSymbol]:
        """索引单个文件."""
        language = self.parser.get_language_for_file(file_path)
        if not language:
            return []

        try:
            content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return []

        if len(content) > MAX_FILE_SIZE:
            return []

        tree = self.parser.parse(content, language)
        symbols = self.extractor.extract(tree, content, language, file_path)
        return symbols

    def get_symbols(self, repo_path: str) -> list[CodeSymbol]:
        """获取已索引的符号."""
        return self._indexed_symbols.get(repo_path, [])

    def get_symbol_by_name(
        self, repo_path: str, name: str
    ) -> CodeSymbol | None:
        """按名称查找符号."""
        for sym in self._indexed_symbols.get(repo_path, []):
            if sym.name == name:
                return sym
        return None

    def get_file_tree(self, repo_path: str) -> dict:
        """获取仓库文件树."""
        root = Path(repo_path)
        if not root.exists():
            return {"name": repo_path, "children": []}

        return self._build_tree(root, root)

    def _build_tree(self, path: Path, root: Path, depth: int = 0) -> dict:
        """递归构建文件树."""
        node = {
            "name": path.name or str(path),
            "path": str(path.relative_to(root)) if path != root else ".",
            "is_dir": path.is_dir(),
        }

        if path.is_dir() and depth < 5:
            if path.name in IGNORE_DIRS:
                return node

            children = []
            try:
                for child in sorted(path.iterdir()):
                    if child.name.startswith(".") and child.name not in (".github",):
                        continue
                    if child.name in IGNORE_FILES:
                        continue
                    children.append(self._build_tree(child, root, depth + 1))
            except PermissionError:
                pass

            node["children"] = children

        return node

    def _walk_code_files(self, root: Path):
        """遍历所有代码文件."""
        for dirpath, dirnames, filenames in os.walk(root):
            # 过滤忽略目录
            dirnames[:] = [
                d for d in dirnames
                if d not in IGNORE_DIRS and not d.startswith(".")
            ]

            for filename in filenames:
                if filename in IGNORE_FILES:
                    continue

                file_path = Path(dirpath) / filename
                language = self.parser.get_language_for_file(filename)
                if language:
                    yield file_path


# 全局单例
repo_indexer = RepoIndexer()
