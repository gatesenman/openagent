"""知识库 API / Knowledge endpoints.

接口:
  GET    /api/knowledge              知识条目列表
  POST   /api/knowledge              创建知识条目
  GET    /api/knowledge/{id}         获取知识条目
  DELETE /api/knowledge/{id}         删除知识条目
  POST   /api/knowledge/search       搜索知识
  POST   /api/knowledge/agents-md    解析 AGENTS.md
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.knowledge.knowledge_manager import knowledge_manager

router = APIRouter()


class KnowledgeCreate(BaseModel):
    name: str
    content: str
    scope: str = "user"
    repo_path: str = ""
    tags: list[str] = []
    pinned: bool = False


class KnowledgeSearch(BaseModel):
    query: str
    top_k: int = 10


class AgentsMdRequest(BaseModel):
    repo_path: str


@router.get("/")
async def list_knowledge(
    scope: str | None = None,
    repo_path: str | None = None,
):
    """获取知识条目列表."""
    entries = knowledge_manager.list_entries(scope=scope, repo_path=repo_path)
    return {
        "entries": [e.to_dict() for e in entries],
        "total": len(entries),
    }


@router.post("/")
async def create_knowledge(data: KnowledgeCreate):
    """创建知识条目."""
    entry = knowledge_manager.add_entry(
        name=data.name,
        content=data.content,
        scope=data.scope,
        repo_path=data.repo_path,
        tags=data.tags,
        pinned=data.pinned,
    )
    return entry.to_dict()


@router.get("/{entry_id}")
async def get_knowledge(entry_id: str):
    """获取知识条目详情."""
    entry = knowledge_manager.get_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="知识条目不存在")
    return {
        **entry.to_dict(),
        "content": entry.content,  # 完整内容
    }


@router.delete("/{entry_id}")
async def delete_knowledge(entry_id: str):
    """删除知识条目."""
    ok = knowledge_manager.delete_entry(entry_id)
    if not ok:
        raise HTTPException(status_code=404, detail="知识条目不存在")
    return {"message": "已删除"}


@router.post("/search")
async def search_knowledge(data: KnowledgeSearch):
    """搜索知识条目."""
    results = knowledge_manager.search(data.query, data.top_k)
    return {
        "results": [e.to_dict() for e in results],
        "total": len(results),
    }


@router.post("/agents-md")
async def parse_agents_md(data: AgentsMdRequest):
    """解析仓库的 AGENTS.md 配置.

    AGENTS.md 是仓库级 Agent 配置标准。
    """
    config = knowledge_manager.parse_agents_md(data.repo_path)
    return config.to_dict()
