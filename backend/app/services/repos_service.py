"""仓库管理服务 / Repository management service.

管理已连接的 Git 仓库，触发 DeepWiki 索引和 CodeMap 分析。
"""

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class IndexStatus(str, Enum):
    PENDING = "pending"
    INDEXING = "indexing"
    READY = "ready"
    FAILED = "failed"


@dataclass
class Repository:
    """已连接的仓库."""
    id: str
    name: str  # owner/repo
    url: str
    default_branch: str = "main"
    language: str = ""
    description: str = ""
    deepwiki_status: IndexStatus = IndexStatus.PENDING
    codemap_status: IndexStatus = IndexStatus.PENDING
    last_indexed_at: float | None = None
    created_at: float = field(default_factory=time.time)
    settings: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "default_branch": self.default_branch,
            "language": self.language,
            "description": self.description,
            "deepwiki_status": self.deepwiki_status.value,
            "codemap_status": self.codemap_status.value,
            "last_indexed_at": self.last_indexed_at,
            "created_at": self.created_at,
            "settings": self.settings,
        }


class ReposService:
    """仓库管理."""

    def __init__(self):
        self._repos: dict[str, Repository] = {}

    def list_repos(self, language: str | None = None) -> list[dict]:
        results = []
        for repo in self._repos.values():
            if language and repo.language != language:
                continue
            results.append(repo.to_dict())
        return results

    def get_repo(self, repo_id: str) -> Repository | None:
        return self._repos.get(repo_id)

    def add_repo(
        self, name: str, url: str, default_branch: str = "main",
        language: str = "", description: str = "",
    ) -> Repository:
        repo = Repository(
            id=str(uuid.uuid4()),
            name=name,
            url=url,
            default_branch=default_branch,
            language=language,
            description=description,
        )
        self._repos[repo.id] = repo
        logger.info("仓库已添加: %s", name)
        return repo

    def remove_repo(self, repo_id: str) -> bool:
        if repo_id in self._repos:
            del self._repos[repo_id]
            return True
        return False

    async def trigger_deepwiki_index(self, repo_id: str) -> dict:
        """触发 DeepWiki 索引."""
        repo = self._repos.get(repo_id)
        if not repo:
            raise ValueError("仓库不存在")
        repo.deepwiki_status = IndexStatus.INDEXING
        # Phase 1: 模拟索引
        repo.deepwiki_status = IndexStatus.READY
        repo.last_indexed_at = time.time()
        return {"status": "indexing", "repo": repo.name}

    async def trigger_codemap_analysis(self, repo_id: str) -> dict:
        """触发 CodeMap 分析."""
        repo = self._repos.get(repo_id)
        if not repo:
            raise ValueError("仓库不存在")
        repo.codemap_status = IndexStatus.INDEXING
        repo.codemap_status = IndexStatus.READY
        return {"status": "analyzing", "repo": repo.name}

    def search_repos(self, query: str) -> list[dict]:
        """搜索仓库."""
        results = []
        query_lower = query.lower()
        for repo in self._repos.values():
            if (query_lower in repo.name.lower()
                or query_lower in repo.description.lower()):
                results.append(repo.to_dict())
        return results


repos_service = ReposService()
