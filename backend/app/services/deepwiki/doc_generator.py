"""文档生成器 / Documentation generator.

使用 LLM 生成符号级 5 段式文档（复刻 DeepWiki 格式）：
Definition / Example Usages / Notes / See Also / Follow-up Questions
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any

from app.services.deepwiki.symbol_extractor import CodeSymbol

logger = logging.getLogger(__name__)


@dataclass
class SymbolDoc:
    """符号文档（DeepWiki 5段式格式）."""
    symbol_name: str
    symbol_kind: str
    file_path: str
    definition: str = ""
    example_usages: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    see_also: list[str] = field(default_factory=list)
    follow_up_questions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "symbol_name": self.symbol_name,
            "symbol_kind": self.symbol_kind,
            "file_path": self.file_path,
            "definition": self.definition,
            "example_usages": self.example_usages,
            "notes": self.notes,
            "see_also": self.see_also,
            "follow_up_questions": self.follow_up_questions,
        }


DOC_PROMPT = """你是一个代码文档专家。为以下代码符号生成文档。

符号: {name} ({kind})
文件: {file_path}
签名: {signature}
{docstring_section}

源码:
```{language}
{code}
```

请以 JSON 格式返回以下5个部分：
{{
    "definition": "用1-3句话描述这个符号的作用和功能",
    "example_usages": ["代码使用示例1", "代码使用示例2"],
    "notes": ["使用注意事项1", "注意事项2"],
    "see_also": ["相关符号名1", "相关符号名2"],
    "follow_up_questions": ["深入问题1?", "深入问题2?", "深入问题3?"]
}}
"""


class DocGenerator:
    """符号文档生成器.

    使用 LLM 为代码符号生成 DeepWiki 5段式文档。
    如果没有 LLM API key，返回模板化的 mock 文档。
    """

    async def generate(
        self,
        symbol: CodeSymbol,
        context_code: str = "",
        llm_client: Any = None,
        model: str = "gpt-4o",
    ) -> SymbolDoc:
        """为单个符号生成完整文档."""
        if llm_client:
            try:
                return await self._generate_with_llm(
                    symbol, context_code, llm_client, model
                )
            except Exception as e:
                logger.warning("LLM 文档生成失败，使用 mock: %s", e)

        return self._generate_mock(symbol)

    async def generate_batch(
        self,
        symbols: list[CodeSymbol],
        llm_client: Any = None,
        model: str = "gpt-4o",
        concurrency: int = 5,
    ) -> list[SymbolDoc]:
        """批量生成文档."""
        import asyncio

        semaphore = asyncio.Semaphore(concurrency)
        results: list[SymbolDoc] = []

        async def gen_one(sym: CodeSymbol) -> SymbolDoc:
            async with semaphore:
                return await self.generate(
                    sym, sym.signature, llm_client, model
                )

        tasks = [gen_one(s) for s in symbols]
        results = await asyncio.gather(*tasks)
        return list(results)

    async def _generate_with_llm(
        self,
        symbol: CodeSymbol,
        context_code: str,
        llm_client: Any,
        model: str,
    ) -> SymbolDoc:
        """使用 LLM 生成文档."""
        docstring_section = (
            f"文档字符串: {symbol.docstring}" if symbol.docstring else ""
        )

        prompt = DOC_PROMPT.format(
            name=symbol.name,
            kind=symbol.kind,
            file_path=symbol.file_path,
            signature=symbol.signature,
            docstring_section=docstring_section,
            language=symbol.language,
            code=context_code or symbol.signature,
        )

        response = await llm_client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=2048,
        )

        data = json.loads(response.choices[0].message.content)

        return SymbolDoc(
            symbol_name=symbol.name,
            symbol_kind=symbol.kind,
            file_path=symbol.file_path,
            definition=data.get("definition", ""),
            example_usages=data.get("example_usages", []),
            notes=data.get("notes", []),
            see_also=data.get("see_also", []),
            follow_up_questions=data.get("follow_up_questions", []),
        )

    def _generate_mock(self, symbol: CodeSymbol) -> SymbolDoc:
        """生成模板化的 mock 文档（无 LLM API key 时）."""
        kind_zh = {
            "function": "函数",
            "class": "类",
            "method": "方法",
            "variable": "变量",
            "interface": "接口",
        }.get(symbol.kind, symbol.kind)

        return SymbolDoc(
            symbol_name=symbol.name,
            symbol_kind=symbol.kind,
            file_path=symbol.file_path,
            definition=f"`{symbol.name}` 是一个 {kind_zh}，定义在 `{symbol.file_path}` 第 {symbol.start_line} 行。{f' {symbol.docstring}' if symbol.docstring else ''}",
            example_usages=[
                f"```{symbol.language}\n# 基本使用\nresult = {symbol.name}(...)\n```",
                f"```{symbol.language}\n# 示例\n{symbol.signature}\n```",
            ],
            notes=[
                f"该{kind_zh}位于 {symbol.file_path}:{symbol.start_line}-{symbol.end_line}",
                "请配置 LLM API Key 以生成更详细的文档",
            ],
            see_also=[f"相关{kind_zh}请查看同模块其他定义"],
            follow_up_questions=[
                f"`{symbol.name}` 的参数和返回值是什么？",
                f"`{symbol.name}` 在哪些地方被使用？",
                f"如何扩展或修改 `{symbol.name}`？",
            ],
        )
