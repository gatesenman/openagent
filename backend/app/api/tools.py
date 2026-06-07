"""工具 API / Tool endpoints.

工具注册、查询和直接执行（MCP兼容）。
"""

from fastapi import APIRouter

from app.schemas.tool import ToolExecuteRequest, ToolExecuteResponse, ToolSchema
from app.services.tool_service import tool_service

router = APIRouter()


@router.get("/")
async def list_tools():
    """列出所有可用工具（MCP Tool 列表）."""
    tools = tool_service.list_tools()
    return {"tools": tools, "total": len(tools)}


@router.get("/{tool_name}")
async def get_tool(tool_name: str):
    """获取工具详情."""
    tool = tool_service.get_tool(tool_name)
    if not tool:
        return {"error": f"工具不存在: {tool_name}"}
    return {
        "name": tool.name,
        "description": tool.description,
        "description_zh": tool.description_zh,
        "parameters": tool.parameters,
        "category": tool.category,
    }


@router.post("/execute", response_model=ToolExecuteResponse)
async def execute_tool(data: ToolExecuteRequest, session_id: str = ""):
    """在沙箱中执行工具."""
    if not session_id:
        return ToolExecuteResponse(
            success=False,
            output="",
            error="需要提供 session_id 参数",
        )

    result = await tool_service.execute_tool(
        session_id=session_id,
        tool_name=data.name,
        arguments=data.arguments,
    )
    return ToolExecuteResponse(
        success=result.success,
        output=result.output,
        error=result.error,
        duration_ms=result.duration_ms,
    )


@router.get("/mcp/list")
async def mcp_list_tools():
    """MCP 协议格式的工具列表."""
    return {"tools": tool_service.get_mcp_tools()}
