"""Agent 管理 API / Agent management endpoints."""

from fastapi import APIRouter

from app.schemas.agent import AgentConfig
from app.sandbox.manager import sandbox_manager

router = APIRouter()


@router.get("/")
async def agent_info():
    """获取 Agent 信息和配置."""
    return {
        "name": "OpenAgent",
        "version": "0.1.0",
        "capabilities": [
            "planning",      # 规划
            "coding",        # 编码
            "testing",       # 测试
            "debugging",     # 调试
            "deployment",    # 部署
            "code_review",   # 代码审查
            "documentation", # 文档生成
        ],
        "modes": [
            {"id": "localhost", "name": "本地模式", "description": "使用本地LLM（Ollama）"},
            {"id": "cascade", "name": "Cascade模式", "description": "编辑器集成模式"},
            {"id": "cloud", "name": "云端模式", "description": "使用远程API（OpenAI/DeepSeek/Claude）"},
        ],
        "models": [
            {"id": "gpt-4o", "provider": "openai", "name": "GPT-4o"},
            {"id": "deepseek-chat", "provider": "deepseek", "name": "DeepSeek Chat"},
            {"id": "deepseek-coder", "provider": "deepseek", "name": "DeepSeek Coder"},
            {"id": "qwen-plus", "provider": "qwen", "name": "Qwen Plus"},
            {"id": "claude-sonnet-4", "provider": "claude", "name": "Claude Sonnet 4"},
        ],
    }


@router.get("/sandboxes")
async def list_sandboxes():
    """列出所有活跃的沙箱虚拟环境."""
    sandboxes = await sandbox_manager.list_sandboxes()
    return {
        "sandboxes": sandboxes,
        "total": len(sandboxes),
    }


@router.get("/config")
async def get_default_config():
    """获取默认 Agent 配置."""
    config = AgentConfig()
    return config.model_dump()
