"""Agent 发现协议 API / Agent discovery endpoints.

实现 llms.txt / agents.txt / .well-known/agent.json 标准。
参考规划文档中行业标准分析。
"""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.core.config import settings

router = APIRouter()


LLMS_TXT = """# OpenAgent
> AI-driven full lifecycle software development platform

## Docs
- [API Documentation](/docs): FastAPI auto-generated API docs
- [Agent Configuration](/AGENTS.md): Agent behavior rules and settings

## Capabilities
- Code Generation: Full lifecycle code generation with sandbox execution
- Code Review: Automated PR review with security checks
- DeepWiki: Repository-level auto documentation
- CodeMap: Code structure visualization
- Testing: Automated test generation and execution
- Debugging: Error analysis and auto-fix
- Deployment: CI/CD pipeline management

## Models
- GPT-4o (OpenAI)
- DeepSeek-V3 (DeepSeek)
- Qwen-Max (Alibaba)
- Claude-3.5-Sonnet (Anthropic)
- Ollama (Local)

## Protocols
- MCP: Model Context Protocol for tool connections
- A2A: Agent-to-Agent protocol for multi-agent collaboration
- AG-UI: Agent-User Interaction protocol for event streaming
- JSON-RPC 2.0: Base communication protocol
"""

AGENTS_TXT = """# agents.txt - OpenAgent Discovery
# Version: 1.0
# Protocol: A2A + MCP + AG-UI

User-agent: *
Allow: /api/
Allow: /mcp/rpc
Allow: /a2a/

Agent-name: OpenAgent
Agent-version: {version}
Agent-description: AI-driven full lifecycle software development platform
Agent-capabilities: code-generation, code-review, testing, debugging, deployment, deepwiki, codemap
Agent-protocols: mcp, a2a, ag-ui, json-rpc-2.0
Agent-card: /.well-known/agent.json

# MCP Server endpoint
MCP-endpoint: /mcp/rpc
MCP-transport: streamable-http

# A2A endpoint
A2A-endpoint: /a2a/
A2A-card: /.well-known/agent.json
""".format(version=settings.APP_VERSION)


@router.get("/llms.txt", response_class=PlainTextResponse)
async def llms_txt():
    """llms.txt — 向 LLM/Agent 声明平台能力."""
    return LLMS_TXT


@router.get("/agents.txt", response_class=PlainTextResponse)
async def agents_txt():
    """agents.txt — Agent 发现协议（类似 robots.txt for AI）."""
    return AGENTS_TXT


@router.get("/.well-known/agent.json")
async def agent_json():
    """Agent Card — A2A/MCP 标准能力声明."""
    return {
        "name": "OpenAgent",
        "version": settings.APP_VERSION,
        "description": "AI-driven full lifecycle software development platform",
        "url": f"http://localhost:8000",
        "protocols": {
            "mcp": {
                "version": "2025-03-26",
                "endpoint": "/mcp/rpc",
                "transport": "streamable-http",
                "capabilities": {
                    "tools": True,
                    "resources": True,
                    "prompts": True,
                },
            },
            "a2a": {
                "version": "0.2.1",
                "endpoint": "/a2a/",
                "capabilities": {
                    "streaming": True,
                    "pushNotifications": False,
                    "stateTransitionHistory": True,
                },
            },
            "ag_ui": {
                "version": "0.1.0",
                "events": [
                    "TEXT_MESSAGE_START",
                    "TEXT_MESSAGE_CONTENT",
                    "TEXT_MESSAGE_END",
                    "TOOL_CALL_START",
                    "TOOL_CALL_ARGS",
                    "TOOL_CALL_END",
                    "STATE_SNAPSHOT",
                    "STATE_DELTA",
                    "RUN_STARTED",
                    "RUN_FINISHED",
                    "RUN_ERROR",
                    "STEP_STARTED",
                    "STEP_FINISHED",
                    "MESSAGES_SNAPSHOT",
                    "RAW",
                    "CUSTOM",
                ],
            },
        },
        "capabilities": [
            {
                "name": "code_generation",
                "description": "Generate code in sandbox with real execution",
            },
            {
                "name": "deepwiki",
                "description": "Auto-generate symbol-level documentation",
            },
            {
                "name": "codemap",
                "description": "Visualize code structure and dependencies",
            },
            {
                "name": "testing",
                "description": "Run tests in isolated sandbox environment",
            },
            {
                "name": "code_review",
                "description": "Automated PR review with security analysis",
            },
        ],
        "authentication": {
            "type": "bearer",
            "token_endpoint": "/api/auth/login",
        },
    }
