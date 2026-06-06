"""OpenAgent API 入口 / Application entry point.

AI 驱动的全生命周期软件开发平台。
所有 Agent 操作在沙箱虚拟环境中执行。
"""

import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api import agents, codemaps, deepwiki, knowledge, playbooks, sessions, tools
from app.core.config import settings
from app.core.database import Base, engine
from app.protocols.agui import AGUIEventBuilder, AGUIEventType
from app.protocols.jsonrpc import JsonRpcRequest, JsonRpcResponse
from app.protocols.a2a import a2a_server, openagent_card
from app.protocols.mcp import mcp_server
from app.sandbox.manager import sandbox_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理."""
    # 启动时
    logger.info("OpenAgent 启动中... version=%s", settings.APP_VERSION)
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表已创建")
    yield
    # 关闭时：清理所有沙箱
    logger.info("正在清理沙箱资源...")
    await sandbox_manager.cleanup_all()
    logger.info("OpenAgent 已关闭")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI 驱动的全生命周期软件开发平台 / AI-driven full lifecycle software development platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载 API 路由
app.include_router(sessions.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(tools.router, prefix="/api/tools", tags=["tools"])
app.include_router(deepwiki.router, prefix="/api/deepwiki", tags=["deepwiki"])
app.include_router(codemaps.router, prefix="/api/codemaps", tags=["codemaps"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["knowledge"])
app.include_router(playbooks.router, prefix="/api/playbooks", tags=["playbooks"])


@app.get("/")
async def root():
    """平台信息."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI 驱动的全生命周期软件开发平台",
        "status": "running",
        "features": {
            "sandbox": settings.SANDBOX_TYPE,
            "llm_provider": settings.LLM_PROVIDER,
            "mcp_enabled": settings.MCP_ENABLED,
        },
    }


@app.get("/health")
async def health():
    """健康检查."""
    sandboxes = await sandbox_manager.list_sandboxes()
    return {
        "status": "ok",
        "active_sandboxes": len(sandboxes),
    }


@app.websocket("/ws/terminal/{session_id}")
async def terminal_websocket(websocket: WebSocket, session_id: str):
    """终端 WebSocket 流.

    用户通过此接口实时查看和操作沙箱内的终端。
    参考 Devin 的终端面板：Agent 在沙箱中执行的命令实时显示。
    """
    await websocket.accept()
    logger.info("终端 WebSocket 连接: session=%s", session_id)

    sandbox = await sandbox_manager.get_sandbox(session_id)
    if not sandbox:
        await websocket.send_json({"type": "error", "message": "沙箱不存在"})
        await websocket.close()
        return

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "exec":
                command = msg.get("command", "")
                # 流式执行命令
                async for output in sandbox.exec_stream(command):
                    await websocket.send_json({
                        "type": "output",
                        "content": output,
                    })
                await websocket.send_json({"type": "exec_done"})

            elif msg.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info("终端 WebSocket 断开: session=%s", session_id)
    except Exception as e:
        logger.error("终端 WebSocket 异常: %s", e)
        try:
            await websocket.close()
        except Exception:
            pass


@app.websocket("/ws/events/{session_id}")
async def events_websocket(websocket: WebSocket, session_id: str):
    """事件 WebSocket 流.

    实时推送 Agent 操作事件（Worklog 实时更新）。
    """
    await websocket.accept()
    logger.info("事件 WebSocket 连接: session=%s", session_id)

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "subscribe":
                await websocket.send_json({
                    "type": "subscribed",
                    "session_id": session_id,
                })

            elif msg.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        logger.info("事件 WebSocket 断开: session=%s", session_id)
    except Exception as e:
        logger.error("事件 WebSocket 异常: %s", e)


# ==================== MCP 协议端点 ====================


@app.post("/mcp/rpc")
async def mcp_rpc_handler(request: dict):
    """MCP JSON-RPC 端点.

    外部 Agent/IDE 通过此端点调用 OpenAgent 的 MCP Server 能力。
    """
    try:
        rpc_req = JsonRpcRequest.from_dict(request)
        rpc_resp = await mcp_server.handle_request(rpc_req)
        return rpc_resp.to_dict()
    except Exception as e:
        return JsonRpcResponse.failure(
            request.get("id"), -32603, f"MCP 处理异常: {e}"
        ).to_dict()


@app.get("/mcp/info")
async def mcp_info():
    """MCP Server 信息."""
    return {
        "name": mcp_server.name,
        "version": mcp_server.version,
        "protocol_version": "2025-03-26",
        "capabilities": {
            "tools": True,
            "resources": True,
            "prompts": True,
        },
    }


@app.get("/api/protocols")
async def protocols_status():
    """协议层状态概览."""
    return {
        "protocols": [
            {
                "name": "JSON-RPC 2.0",
                "status": "active",
                "endpoint": "/mcp/rpc",
            },
            {
                "name": "MCP",
                "status": "active",
                "version": "2025-03-26",
                "endpoint": "/mcp/rpc",
            },
            {
                "name": "AG-UI",
                "status": "active",
                "events": len(AGUIEventType),
                "transport": "SSE + WebSocket",
            },
            {
                "name": "A2A",
                "status": "active",
                "version": "0.2.2",
                "endpoint": "/a2a/rpc",
                "agent_card": "/.well-known/agent.json",
            },
        ],
    }


# ==================== A2A 协议端点 ====================


@app.get("/.well-known/agent.json")
async def agent_card():
    """A2A Agent Card — Agent 能力声明.

    外部 Agent 通过此端点发现 OpenAgent 的能力。
    """
    return a2a_server.get_agent_card()


@app.post("/a2a/rpc")
async def a2a_rpc_handler(request: dict):
    """A2A JSON-RPC 端点.

    处理 Agent 间协作请求:
    - tasks/send: 接收任务
    - tasks/get: 查询任务状态
    - tasks/cancel: 取消任务
    """
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id")

    try:
        if method == "tasks/send":
            result = await a2a_server.handle_send(params)
        elif method == "tasks/get":
            result = await a2a_server.handle_get(params)
        elif method == "tasks/cancel":
            result = await a2a_server.handle_cancel(params)
        else:
            return JsonRpcResponse.failure(
                req_id, -32601, f"方法不存在: {method}"
            ).to_dict()

        return JsonRpcResponse.success(req_id, result).to_dict()
    except Exception as e:
        return JsonRpcResponse.failure(
            req_id, -32603, f"A2A 处理异常: {e}"
        ).to_dict()
