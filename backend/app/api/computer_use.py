"""Computer Use API — browser/desktop automation endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from app.agent.computer_use import (
    ActionType,
    BrowserBackend,
    ComputerAction,
    computer_use_engine,
)

router = APIRouter()


class CreateSessionRequest(BaseModel):
    sandbox_id: str
    backend: str = "cdp"
    viewport_width: int = 1280
    viewport_height: int = 800


class ActionRequest(BaseModel):
    action_type: str
    x: int | None = None
    y: int | None = None
    text: str | None = None
    key: str | None = None
    url: str | None = None
    scroll_direction: str | None = None
    description: str = ""


@router.post("/sessions/{session_id}")
async def create_computer_session(session_id: str, req: CreateSessionRequest):
    """Create a computer use session for a sandbox."""
    backend = BrowserBackend(req.backend)
    session = computer_use_engine.create_session(
        session_id, req.sandbox_id, backend, (req.viewport_width, req.viewport_height)
    )
    return {
        "session_id": session.session_id,
        "backend": session.backend.value,
        "viewport": f"{session.viewport_width}x{session.viewport_height}",
    }


@router.post("/sessions/{session_id}/screenshot")
async def take_screenshot(session_id: str):
    """Capture screenshot from sandbox display."""
    b64 = await computer_use_engine.take_screenshot(session_id)
    return {"screenshot_b64": b64}


@router.post("/sessions/{session_id}/action")
async def execute_action(session_id: str, req: ActionRequest):
    """Execute a computer use action."""
    action = ComputerAction(
        action_type=ActionType(req.action_type),
        x=req.x,
        y=req.y,
        text=req.text,
        key=req.key,
        url=req.url,
        scroll_direction=req.scroll_direction,
        description=req.description,
    )
    result = await computer_use_engine.execute_action(session_id, action)
    return result


@router.post("/sessions/{session_id}/vision-step")
async def vision_loop_step(session_id: str, task: str = ""):
    """Execute one step of the vision loop."""
    result = await computer_use_engine.vision_loop_step(session_id, task)
    return result


@router.delete("/sessions/{session_id}")
async def close_computer_session(session_id: str):
    """Close a computer use session."""
    computer_use_engine.close_session(session_id)
    return {"status": "closed"}
