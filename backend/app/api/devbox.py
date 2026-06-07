"""Devbox 沙箱执行 API / Sandbox execution endpoints.

提供沙箱内的命令执行、文件读写、桌面流等核心接口。
Agent 的所有操作都通过此 API 在沙箱虚拟环境中执行。
"""

import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.sandbox.manager import sandbox_manager

logger = logging.getLogger(__name__)
router = APIRouter()


class ExecRequest(BaseModel):
    command: str
    timeout: int = 30
    workdir: str | None = None


class FileReadRequest(BaseModel):
    path: str
    encoding: str = "utf-8"


class FileWriteRequest(BaseModel):
    path: str
    content: str
    encoding: str = "utf-8"
    create_dirs: bool = True


class FileDeleteRequest(BaseModel):
    path: str


# ---------------------------------------------------------------------------
# 命令执行
# ---------------------------------------------------------------------------

@router.post("/{session_id}/exec")
async def exec_command(session_id: str, req: ExecRequest):
    """在沙箱中执行命令.

    Agent 通过此接口在隔离的虚拟环境中执行 shell 命令。
    支持超时控制和工作目录切换。
    """
    sandbox = await sandbox_manager.get_sandbox(session_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="沙箱不存在，请先创建会话")

    try:
        result = await sandbox.exec(req.command)
        return {
            "session_id": session_id,
            "command": req.command,
            "exit_code": result.get("exit_code", 0),
            "stdout": result.get("stdout", ""),
            "stderr": result.get("stderr", ""),
        }
    except Exception as e:
        logger.error("沙箱执行失败 [%s]: %s", session_id, e)
        raise HTTPException(status_code=500, detail=f"执行失败: {e}")


# ---------------------------------------------------------------------------
# 文件操作
# ---------------------------------------------------------------------------

@router.post("/{session_id}/file/read")
async def read_file(session_id: str, req: FileReadRequest):
    """从沙箱中读取文件."""
    sandbox = await sandbox_manager.get_sandbox(session_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="沙箱不存在")

    try:
        content = await sandbox.read_file(req.path)
        return {
            "path": req.path,
            "content": content,
            "encoding": req.encoding,
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"文件不存在: {req.path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取失败: {e}")


@router.post("/{session_id}/file/write")
async def write_file(session_id: str, req: FileWriteRequest):
    """向沙箱中写入文件."""
    sandbox = await sandbox_manager.get_sandbox(session_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="沙箱不存在")

    try:
        await sandbox.write_file(req.path, req.content)
        return {
            "path": req.path,
            "status": "written",
            "size": len(req.content),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"写入失败: {e}")


@router.post("/{session_id}/file/delete")
async def delete_file(session_id: str, req: FileDeleteRequest):
    """删除沙箱中的文件."""
    sandbox = await sandbox_manager.get_sandbox(session_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="沙箱不存在")

    try:
        result = await sandbox.exec(f"rm -f {req.path}")
        return {"path": req.path, "status": "deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除失败: {e}")


@router.get("/{session_id}/file/list")
async def list_files(session_id: str, path: str = "/workspace"):
    """列出沙箱中指定目录的文件."""
    sandbox = await sandbox_manager.get_sandbox(session_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="沙箱不存在")

    try:
        result = await sandbox.exec(f"find {path} -maxdepth 2 -type f | head -200")
        files = [f for f in result.get("stdout", "").strip().split("\n") if f]
        return {"path": path, "files": files, "count": len(files)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"列出文件失败: {e}")


# ---------------------------------------------------------------------------
# 沙箱状态
# ---------------------------------------------------------------------------

@router.get("/{session_id}/status")
async def sandbox_status(session_id: str):
    """获取沙箱状态信息."""
    sandbox = await sandbox_manager.get_sandbox(session_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="沙箱不存在")

    status = await sandbox.status()
    return {
        "session_id": session_id,
        "status": status,
        "type": sandbox.__class__.__name__,
    }


@router.get("/{session_id}/desktop")
async def desktop_info(session_id: str):
    """获取桌面流连接信息 (VNC/noVNC).

    Phase 1: 返回连接参数。
    Phase 2: 实际 WebSocket 升级为 VNC 流。
    """
    sandbox = await sandbox_manager.get_sandbox(session_id)
    if not sandbox:
        raise HTTPException(status_code=404, detail="沙箱不存在")

    return {
        "session_id": session_id,
        "vnc_url": f"ws://localhost:6080/websockify?session={session_id}",
        "resolution": "1920x1080",
        "protocol": "noVNC",
        "status": "available",
    }
