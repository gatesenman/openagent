"""DeepWiki API — 符号级代码文档引擎.

接口:
  GET  /api/deepwiki              状态概览
  POST /api/deepwiki/index        索引仓库
  GET  /api/deepwiki/symbols      查询符号列表
  GET  /api/deepwiki/symbols/{name} 获取符号文档
  POST /api/deepwiki/search       语义搜索
  GET  /api/deepwiki/tree         文件树
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.deepwiki.doc_generator import DocGenerator
from app.services.deepwiki.embedding_service import embedding_service
from app.services.deepwiki.indexer import repo_indexer

router = APIRouter()


class IndexRequest(BaseModel):
    repo_path: str


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10


@router.get("/")
async def deepwiki_status():
    """DeepWiki 状态概览."""
    indexed_repos = list(repo_indexer._indexed_symbols.keys())
    total_symbols = sum(
        len(syms) for syms in repo_indexer._indexed_symbols.values()
    )
    return {
        "status": "ready",
        "indexed_repos": len(indexed_repos),
        "repos": indexed_repos,
        "total_symbols": total_symbols,
    }


@router.post("/index")
async def index_repo(req: IndexRequest):
    """索引仓库（解析 AST → 提取符号 → 生成 embedding）."""
    result = await repo_indexer.index_repo(req.repo_path)
    return {
        "total_files": result.total_files,
        "indexed_files": result.indexed_files,
        "total_symbols": result.total_symbols,
        "languages": result.languages,
        "errors": result.errors[:10],
    }


@router.get("/symbols")
async def list_symbols(repo_path: str, kind: str | None = None):
    """查询已索引的符号列表."""
    symbols = repo_indexer.get_symbols(repo_path)
    if kind:
        symbols = [s for s in symbols if s.kind == kind]
    return {
        "symbols": [s.to_dict() for s in symbols],
        "total": len(symbols),
    }


@router.get("/symbols/{name}")
async def get_symbol_doc(name: str, repo_path: str):
    """获取符号的 5 段式文档."""
    symbol = repo_indexer.get_symbol_by_name(repo_path, name)
    if not symbol:
        raise HTTPException(status_code=404, detail=f"符号未找到: {name}")

    doc_gen = DocGenerator()
    doc = await doc_gen.generate(symbol)
    return doc.to_dict()


@router.post("/search")
async def semantic_search(req: SearchRequest):
    """语义搜索符号."""
    results = await embedding_service.search(req.query, req.top_k)
    return {
        "results": [
            {
                "file_path": r.file_path,
                "symbol_name": r.symbol_name,
                "score": round(r.score, 4),
                "content": r.content,
            }
            for r in results
        ],
        "total": len(results),
    }


@router.get("/tree")
async def file_tree(repo_path: str):
    """获取仓库文件树."""
    tree = repo_indexer.get_file_tree(repo_path)
    return tree
