"""MCP 工具市场 API / MCP Marketplace endpoints."""

from fastapi import APIRouter, HTTPException

from app.services.mcp_marketplace import mcp_marketplace

router = APIRouter()


@router.get("/servers")
async def list_servers(category: str | None = None):
    """列出所有 MCP Server."""
    return [s.to_dict() for s in mcp_marketplace.list_servers(category)]


@router.get("/servers/{server_id}")
async def get_server(server_id: str):
    """获取 MCP Server 详情."""
    server = mcp_marketplace.get_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server 未找到")
    return server.to_dict()


@router.post("/servers/{server_id}/install")
async def install_server(server_id: str):
    """安装 MCP Server."""
    server = mcp_marketplace.install_server(server_id)
    if not server:
        raise HTTPException(status_code=404, detail="Server 未找到")
    return server.to_dict()


@router.post("/servers/{server_id}/uninstall")
async def uninstall_server(server_id: str):
    """卸载 MCP Server."""
    if not mcp_marketplace.uninstall_server(server_id):
        raise HTTPException(status_code=400, detail="无法卸载内置 Server")
    return {"uninstalled": True}


@router.post("/servers/{server_id}/toggle")
async def toggle_server(server_id: str, enabled: bool = True):
    """启用/禁用 MCP Server."""
    server = mcp_marketplace.toggle_server(server_id, enabled)
    if not server:
        raise HTTPException(status_code=404, detail="Server 未找到")
    return server.to_dict()


@router.get("/tools")
async def list_installed_tools():
    """列出所有已安装的工具."""
    return mcp_marketplace.get_installed_tools()
