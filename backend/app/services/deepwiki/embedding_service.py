"""Embedding 服务 / Embedding service.

生成代码嵌入向量，用于语义搜索。
支持 OpenAI text-embedding-3-small，降级为 TF-IDF。
"""

import logging
import math
from collections import Counter
from dataclasses import dataclass
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """搜索结果."""
    file_path: str
    symbol_name: str
    score: float
    content: str


class EmbeddingService:
    """代码嵌入向量服务.

    用于 DeepWiki 的语义搜索。
    优先使用 OpenAI embedding API，降级为 TF-IDF。
    """

    def __init__(self):
        self._store: list[dict] = []
        self._client: Any = None

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """生成文本嵌入向量."""
        if settings.LLM_API_KEY:
            try:
                return await self._embed_openai(texts)
            except Exception as e:
                logger.warning("OpenAI embedding 失败，降级为 TF-IDF: %s", e)

        return self._embed_tfidf(texts)

    async def _embed_openai(self, texts: list[str]) -> list[list[float]]:
        """使用 OpenAI API 生成 embedding."""
        if not self._client:
            from openai import AsyncOpenAI
            self._client = AsyncOpenAI(api_key=settings.LLM_API_KEY)

        response = await self._client.embeddings.create(
            model="text-embedding-3-small",
            input=texts,
        )
        return [item.embedding for item in response.data]

    def _embed_tfidf(self, texts: list[str]) -> list[list[float]]:
        """TF-IDF 降级方案."""
        # 构建词汇表
        all_tokens: set[str] = set()
        tokenized = []
        for text in texts:
            tokens = self._tokenize(text)
            tokenized.append(tokens)
            all_tokens.update(tokens)

        vocab = sorted(all_tokens)
        vocab_idx = {w: i for i, w in enumerate(vocab)}
        dim = min(len(vocab), 256)

        # 计算 IDF
        doc_count = len(texts)
        idf: dict[str, float] = {}
        for word in vocab:
            df = sum(1 for toks in tokenized if word in toks)
            idf[word] = math.log((doc_count + 1) / (df + 1)) + 1

        # 计算 TF-IDF 向量
        embeddings = []
        for tokens in tokenized:
            tf = Counter(tokens)
            vec = [0.0] * dim
            for word, count in tf.items():
                idx = vocab_idx.get(word, -1)
                if 0 <= idx < dim:
                    vec[idx] = count * idf.get(word, 1.0)
            # 归一化
            norm = math.sqrt(sum(v * v for v in vec)) or 1.0
            vec = [v / norm for v in vec]
            embeddings.append(vec)

        return embeddings

    async def index(
        self, texts: list[str], metadata: list[dict]
    ) -> None:
        """索引文本和元数据."""
        embeddings = await self.embed(texts)
        for emb, meta in zip(embeddings, metadata):
            self._store.append({"embedding": emb, **meta})

    async def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        """语义搜索."""
        if not self._store:
            return []

        query_emb = (await self.embed([query]))[0]

        scored = []
        for item in self._store:
            score = self._cosine_similarity(query_emb, item["embedding"])
            scored.append((score, item))

        scored.sort(key=lambda x: x[0], reverse=True)

        return [
            SearchResult(
                file_path=item.get("file_path", ""),
                symbol_name=item.get("symbol_name", ""),
                score=score,
                content=item.get("content", ""),
            )
            for score, item in scored[:top_k]
        ]

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        """简单分词."""
        import re
        # 按非字母数字字符分割，再按驼峰/下划线分割
        words = re.findall(r"[a-zA-Z][a-z]*|[A-Z]+(?=[A-Z][a-z]|\d|\b)|[a-z]+|\d+", text)
        return [w.lower() for w in words if len(w) > 1]

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        """余弦相似度."""
        min_len = min(len(a), len(b))
        dot = sum(a[i] * b[i] for i in range(min_len))
        norm_a = math.sqrt(sum(x * x for x in a[:min_len])) or 1.0
        norm_b = math.sqrt(sum(x * x for x in b[:min_len])) or 1.0
        return dot / (norm_a * norm_b)


# 全局单例
embedding_service = EmbeddingService()
