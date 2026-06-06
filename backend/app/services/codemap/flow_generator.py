"""代码流程图生成器 / Code flow generator.

复刻 Windsurf CodeMap 格式：
编号步骤 + 标题 + 描述 + 源码位置 + 代码片段 + 箭头连接。
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.services.codemap.analyzer import CodeAnalyzer
from app.services.deepwiki.parser import CodeParser
from app.services.deepwiki.symbol_extractor import SymbolExtractor

logger = logging.getLogger(__name__)


@dataclass
class FlowStep:
    """流程步骤（复刻 Windsurf CodeMap）."""
    step_number: int
    title: str
    description: str
    source_file: str
    source_lines: str      # "10-25"
    code_snippet: str
    next_steps: list[int] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "step_number": self.step_number,
            "title": self.title,
            "description": self.description,
            "source_file": self.source_file,
            "source_lines": self.source_lines,
            "code_snippet": self.code_snippet,
            "next_steps": self.next_steps,
        }


class FlowGenerator:
    """代码流程图生成器.

    从入口点追踪调用链，生成编号步骤的流程图。
    复刻 Windsurf CodeMap 的可视化格式。
    """

    def __init__(self):
        self.parser = CodeParser()
        self.extractor = SymbolExtractor()

    async def generate_flow(
        self,
        entry_point: str,
        repo_path: str,
        llm_client: Any = None,
        model: str = "gpt-4o",
    ) -> list[FlowStep]:
        """从入口点生成代码流程.

        Args:
            entry_point: 入口文件或函数名
            repo_path: 仓库路径
        """
        if llm_client:
            try:
                return await self._generate_with_llm(
                    entry_point, repo_path, llm_client, model
                )
            except Exception as e:
                logger.warning("LLM 流程生成失败，使用静态分析: %s", e)

        return self._generate_static(entry_point, repo_path)

    def _generate_static(self, entry_point: str, repo_path: str) -> list[FlowStep]:
        """静态分析生成流程图."""
        steps: list[FlowStep] = []
        root = Path(repo_path)

        # 查找入口文件
        entry_file = self._find_entry_file(entry_point, root)
        if not entry_file:
            return [FlowStep(
                step_number=1,
                title="入口点",
                description=f"未找到入口文件: {entry_point}",
                source_file=entry_point,
                source_lines="1-1",
                code_snippet="# Entry point not found",
            )]

        try:
            content = entry_file.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return []

        language = self.parser.get_language_for_file(str(entry_file))
        if not language:
            return []

        lines = content.split("\n")
        rel_path = str(entry_file.relative_to(root))

        # 解析并提取符号
        tree = self.parser.parse(content, language)
        symbols = self.extractor.extract(tree, content, language, rel_path)

        step_num = 1

        # Step 1: 模块导入
        import_lines = self._find_import_section(lines, language)
        if import_lines:
            start, end = import_lines
            snippet = "\n".join(lines[start:end + 1])
            steps.append(FlowStep(
                step_number=step_num,
                title="模块导入",
                description="导入所需的依赖模块",
                source_file=rel_path,
                source_lines=f"{start + 1}-{end + 1}",
                code_snippet=snippet[:500],
                next_steps=[step_num + 1],
            ))
            step_num += 1

        # Step 2+: 每个主要符号
        for sym in symbols:
            if sym.kind in ("function", "class"):
                snippet_lines = lines[sym.start_line - 1:min(sym.end_line, sym.start_line + 10)]
                steps.append(FlowStep(
                    step_number=step_num,
                    title=f"{sym.kind.capitalize()}: {sym.name}",
                    description=sym.docstring or f"定义 {sym.kind} `{sym.name}`",
                    source_file=rel_path,
                    source_lines=f"{sym.start_line}-{sym.end_line}",
                    code_snippet="\n".join(snippet_lines)[:500],
                    next_steps=[step_num + 1] if step_num < len(symbols) + 1 else [],
                ))
                step_num += 1

        # 最后一步：主执行
        main_line = self._find_main_block(lines, language)
        if main_line is not None:
            snippet = "\n".join(lines[main_line:main_line + 5])
            steps.append(FlowStep(
                step_number=step_num,
                title="主执行入口",
                description="程序主执行逻辑",
                source_file=rel_path,
                source_lines=f"{main_line + 1}-{min(main_line + 5, len(lines))}",
                code_snippet=snippet[:500],
            ))

        return steps

    async def _generate_with_llm(
        self,
        entry_point: str,
        repo_path: str,
        llm_client: Any,
        model: str,
    ) -> list[FlowStep]:
        """使用 LLM 生成更智能的流程图."""
        root = Path(repo_path)
        entry_file = self._find_entry_file(entry_point, root)
        if not entry_file:
            return self._generate_static(entry_point, repo_path)

        content = entry_file.read_text(encoding="utf-8", errors="ignore")
        rel_path = str(entry_file.relative_to(root))

        import json
        prompt = f"""分析以下代码的执行流程，生成编号步骤的流程图。

文件: {rel_path}
```
{content[:5000]}
```

以 JSON 数组格式返回:
[
    {{
        "step_number": 1,
        "title": "步骤标题",
        "description": "步骤描述",
        "source_lines": "10-25",
        "code_snippet": "关键代码片段",
        "next_steps": [2]
    }}
]"""

        response = await llm_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        data = json.loads(response.choices[0].message.content)
        steps_data = data if isinstance(data, list) else data.get("steps", [])

        return [
            FlowStep(
                step_number=s.get("step_number", i + 1),
                title=s.get("title", ""),
                description=s.get("description", ""),
                source_file=rel_path,
                source_lines=s.get("source_lines", ""),
                code_snippet=s.get("code_snippet", ""),
                next_steps=s.get("next_steps", []),
            )
            for i, s in enumerate(steps_data)
        ]

    async def generate_module_overview(self, repo_path: str) -> dict:
        """生成模块概览图."""
        analyzer = CodeAnalyzer()
        modules = analyzer.analyze_directory(repo_path)

        # 按目录层级组织
        overview: dict = {"name": Path(repo_path).name, "type": "root", "children": []}
        dir_map: dict[str, dict] = {"": overview}

        for module in modules:
            parts = Path(module.path).parts
            current = overview

            for i, part in enumerate(parts[:-1]):
                dir_path = "/".join(parts[:i + 1])
                if dir_path not in dir_map:
                    node = {"name": part, "type": "directory", "children": []}
                    current.setdefault("children", []).append(node)
                    dir_map[dir_path] = node
                current = dir_map[dir_path]

            file_node = {
                "name": parts[-1],
                "type": "file",
                "language": module.language,
                "size": module.size_lines,
                "complexity": module.complexity,
                "symbols": module.symbols[:10],
            }
            current.setdefault("children", []).append(file_node)

        return overview

    def _find_entry_file(self, entry_point: str, root: Path) -> Path | None:
        """查找入口文件."""
        # 直接路径
        direct = root / entry_point
        if direct.exists():
            return direct

        # 常见入口
        common_entries = [
            "main.py", "app.py", "index.js", "index.ts",
            "src/main.py", "src/app.py", "src/index.ts",
            "backend/app/main.py", "server.py",
        ]

        for entry in common_entries:
            candidate = root / entry
            if candidate.exists():
                return candidate

        return None

    @staticmethod
    def _find_import_section(lines: list[str], language: str) -> tuple[int, int] | None:
        """找到导入区域."""
        start = None
        end = None

        import_pattern = {
            "python": r"^(?:import|from)\s+",
            "javascript": r"^(?:import|const|require)",
            "typescript": r"^(?:import|const|require)",
            "java": r"^import\s+",
            "go": r'^(?:import\s+|")',
        }.get(language, r"^import\s+")

        for i, line in enumerate(lines):
            if re.match(import_pattern, line.strip()):
                if start is None:
                    start = i
                end = i

        if start is not None and end is not None:
            return (start, end)
        return None

    @staticmethod
    def _find_main_block(lines: list[str], language: str) -> int | None:
        """找到主执行块."""
        patterns = {
            "python": r'^if\s+__name__\s*==\s*["\']__main__["\']',
            "javascript": r"^(?:module\.exports|app\.listen|main\(\))",
            "go": r"^func\s+main\(\)",
            "java": r"public\s+static\s+void\s+main",
        }
        pattern = patterns.get(language)
        if not pattern:
            return None

        for i, line in enumerate(lines):
            if re.search(pattern, line.strip()):
                return i
        return None
