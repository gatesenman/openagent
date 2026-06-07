"""Code Retrieval Pipeline — hybrid search for zero-hallucination context.

Implements the 4-step retrieval pipeline from planning docs:
  Step 1: Intent parsing (extract keywords from user query)
  Step 2: Hybrid retrieval (BM25 keyword + embedding semantic)
  Step 3: Context ranking (multi-factor reranking)
  Step 4: Budget trimming (fit within token budget)
"""

import math
import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CodeChunk:
    """A chunk of code with metadata."""

    file_path: str
    start_line: int
    end_line: int
    content: str
    language: str = ""
    score: float = 0.0
    token_count: int = 0


@dataclass
class RetrievalResult:
    """Result from the code retrieval pipeline."""

    query: str
    chunks: list[CodeChunk] = field(default_factory=list)
    total_tokens: int = 0
    strategy: str = "hybrid"
    keywords_extracted: list[str] = field(default_factory=list)


class IntentParser:
    """Step 1: Parse user query into searchable keywords and semantic queries."""

    # Common programming terms for expansion
    SYNONYM_MAP = {
        "login": ["auth", "signin", "authenticate", "session"],
        "user": ["account", "profile", "member"],
        "api": ["endpoint", "route", "handler"],
        "database": ["db", "model", "schema", "query"],
        "test": ["spec", "unittest", "pytest", "jest"],
        "error": ["exception", "bug", "issue", "fix"],
        "config": ["settings", "env", "configuration"],
    }

    def parse(self, query: str) -> dict[str, Any]:
        """Extract keywords and semantic query from user input."""
        # Tokenize and normalize
        words = re.findall(r"\w+", query.lower())

        # Extract programming keywords
        keywords = [w for w in words if len(w) > 2]

        # Expand with synonyms
        expanded = list(keywords)
        for word in keywords:
            if word in self.SYNONYM_MAP:
                expanded.extend(self.SYNONYM_MAP[word])

        return {
            "keywords": list(set(keywords)),
            "expanded_keywords": list(set(expanded)),
            "semantic_query": query,
            "file_patterns": self._extract_file_patterns(query),
        }

    def _extract_file_patterns(self, query: str) -> list[str]:
        """Extract file path patterns from query."""
        patterns = []
        # Match file references
        file_refs = re.findall(r"[\w/]+\.\w+", query)
        patterns.extend(file_refs)
        return patterns


class BM25Index:
    """BM25 keyword search index for code files."""

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self.k1 = k1
        self.b = b
        self._documents: list[CodeChunk] = []
        self._doc_freqs: Counter = Counter()
        self._doc_lens: list[int] = []
        self._avg_dl: float = 0.0
        self._n_docs: int = 0
        self._inverted_index: dict[str, list[int]] = {}

    def index(self, chunks: list[CodeChunk]) -> None:
        """Build BM25 index from code chunks."""
        self._documents = chunks
        self._n_docs = len(chunks)

        for i, chunk in enumerate(chunks):
            tokens = self._tokenize(chunk.content)
            self._doc_lens.append(len(tokens))
            seen = set()
            for token in tokens:
                if token not in self._inverted_index:
                    self._inverted_index[token] = []
                self._inverted_index[token].append(i)
                if token not in seen:
                    self._doc_freqs[token] += 1
                    seen.add(token)

        self._avg_dl = sum(self._doc_lens) / self._n_docs if self._n_docs else 1.0

    def search(self, query: str, top_k: int = 20) -> list[tuple[CodeChunk, float]]:
        """Search for relevant code chunks using BM25."""
        query_tokens = self._tokenize(query)
        scores: dict[int, float] = {}

        for token in query_tokens:
            if token not in self._inverted_index:
                continue
            df = self._doc_freqs[token]
            idf = math.log((self._n_docs - df + 0.5) / (df + 0.5) + 1)

            for doc_id in self._inverted_index[token]:
                tf = self._documents[doc_id].content.lower().count(token)
                dl = self._doc_lens[doc_id]
                tf_norm = (tf * (self.k1 + 1)) / (
                    tf + self.k1 * (1 - self.b + self.b * dl / self._avg_dl)
                )
                scores[doc_id] = scores.get(doc_id, 0) + idf * tf_norm

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [(self._documents[doc_id], score) for doc_id, score in ranked]

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into lowercase words."""
        return re.findall(r"\w+", text.lower())


class ContextRanker:
    """Step 3: Multi-factor reranking of retrieved chunks.

    Factors (from planning doc):
    - Semantic relevance: 0.4
    - Dependency graph importance: 0.2
    - Recency: 0.15
    - Path match: 0.15
    - Complexity/length: 0.1
    """

    WEIGHTS = {
        "semantic": 0.4,
        "dependency": 0.2,
        "recency": 0.15,
        "path_match": 0.15,
        "complexity": 0.1,
    }

    def rank(
        self,
        chunks: list[tuple[CodeChunk, float]],
        query_keywords: list[str],
        file_patterns: list[str] | None = None,
    ) -> list[CodeChunk]:
        """Rerank chunks using multi-factor scoring."""
        scored = []
        for chunk, base_score in chunks:
            # Semantic score (from BM25/embedding)
            semantic = min(base_score / 10.0, 1.0)

            # Path match score
            path_match = 0.0
            if file_patterns:
                for pattern in file_patterns:
                    if pattern.lower() in chunk.file_path.lower():
                        path_match = 1.0
                        break
            elif query_keywords:
                for kw in query_keywords:
                    if kw.lower() in chunk.file_path.lower():
                        path_match += 0.3
                path_match = min(path_match, 1.0)

            # Complexity score (prefer moderately complex chunks)
            lines = chunk.end_line - chunk.start_line + 1
            complexity = min(lines / 50.0, 1.0) if lines < 100 else 0.5

            # Combined score
            final = (
                self.WEIGHTS["semantic"] * semantic
                + self.WEIGHTS["path_match"] * path_match
                + self.WEIGHTS["complexity"] * complexity
                + self.WEIGHTS["dependency"] * 0.5  # Default mid-score
                + self.WEIGHTS["recency"] * 0.5  # Default mid-score
            )

            chunk.score = final
            scored.append(chunk)

        scored.sort(key=lambda c: c.score, reverse=True)
        return scored


class BudgetTrimmer:
    """Step 4: Trim retrieved context to fit within token budget."""

    def __init__(self, budget_tokens: int = 8000) -> None:
        self.budget = budget_tokens

    def trim(self, chunks: list[CodeChunk]) -> list[CodeChunk]:
        """Select top chunks that fit within budget."""
        selected = []
        used_tokens = 0

        for chunk in chunks:
            # Estimate tokens (~4 chars per token)
            chunk_tokens = len(chunk.content) // 4
            chunk.token_count = chunk_tokens

            if used_tokens + chunk_tokens > self.budget:
                # Try to fit a truncated version
                remaining = self.budget - used_tokens
                if remaining > 200:
                    truncated = CodeChunk(
                        file_path=chunk.file_path,
                        start_line=chunk.start_line,
                        end_line=chunk.start_line + remaining // 20,
                        content=chunk.content[: remaining * 4],
                        language=chunk.language,
                        score=chunk.score,
                        token_count=remaining,
                    )
                    selected.append(truncated)
                break

            selected.append(chunk)
            used_tokens += chunk_tokens

        return selected


class CodeRetrievalPipeline:
    """Complete hybrid code retrieval pipeline.

    Combines BM25 keyword search with semantic search,
    reranks results, and trims to token budget.
    """

    def __init__(self, budget_tokens: int = 8000) -> None:
        self.intent_parser = IntentParser()
        self.bm25 = BM25Index()
        self.ranker = ContextRanker()
        self.trimmer = BudgetTrimmer(budget_tokens)
        self._indexed = False

    def index_codebase(self, files: dict[str, str], chunk_size: int = 50) -> int:
        """Index a codebase using sliding window chunking.

        Args:
            files: Map of file_path -> file_content
            chunk_size: Lines per chunk (sliding window)

        Returns:
            Number of chunks indexed
        """
        chunks = []
        for filepath, content in files.items():
            lang = filepath.rsplit(".", 1)[-1] if "." in filepath else ""
            lines = content.split("\n")

            # Sliding window chunking (recommended by planning doc)
            stride = chunk_size // 2  # 50% overlap
            for start in range(0, len(lines), stride):
                end = min(start + chunk_size, len(lines))
                chunk_content = "\n".join(lines[start:end])
                if chunk_content.strip():
                    chunks.append(
                        CodeChunk(
                            file_path=filepath,
                            start_line=start + 1,
                            end_line=end,
                            content=chunk_content,
                            language=lang,
                        )
                    )

        self.bm25.index(chunks)
        self._indexed = True
        return len(chunks)

    def retrieve(self, query: str, top_k: int = 10) -> RetrievalResult:
        """Run the full 4-step retrieval pipeline."""
        if not self._indexed:
            return RetrievalResult(query=query)

        # Step 1: Intent parsing
        intent = self.intent_parser.parse(query)

        # Step 2: BM25 keyword search
        search_query = " ".join(intent["expanded_keywords"])
        bm25_results = self.bm25.search(search_query, top_k=top_k * 2)

        # Step 3: Context ranking
        ranked = self.ranker.rank(
            bm25_results,
            intent["keywords"],
            intent["file_patterns"],
        )

        # Step 4: Budget trimming
        trimmed = self.trimmer.trim(ranked[:top_k])

        return RetrievalResult(
            query=query,
            chunks=trimmed,
            total_tokens=sum(c.token_count for c in trimmed),
            keywords_extracted=intent["keywords"],
        )

    def format_context(self, result: RetrievalResult) -> str:
        """Format retrieval results for injection into Agent system prompt."""
        if not result.chunks:
            return ""

        parts = ["<relevant_code>"]
        for chunk in result.chunks:
            parts.append(
                f"<file path=\"{chunk.file_path}\" "
                f"lines=\"{chunk.start_line}-{chunk.end_line}\" "
                f"score=\"{chunk.score:.2f}\">"
            )
            parts.append(chunk.content)
            parts.append("</file>")
        parts.append("</relevant_code>")
        return "\n".join(parts)


# Singleton
code_retrieval = CodeRetrievalPipeline()
