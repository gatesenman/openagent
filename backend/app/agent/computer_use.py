"""Computer Use System — browser/desktop automation via vision loop.

Implements the screenshot -> multimodal LLM -> action -> screenshot
cycle for UI testing, OAuth login, and web debugging within the sandbox.
"""

import base64
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ActionType(str, Enum):
    """Supported computer use actions."""

    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    TYPE = "type"
    KEY = "key"
    SCROLL = "scroll"
    SCREENSHOT = "screenshot"
    DRAG = "drag"
    WAIT = "wait"
    NAVIGATE = "navigate"


class BrowserBackend(str, Enum):
    CDP = "cdp"  # Chrome DevTools Protocol
    VNC = "vnc"  # VNC remote desktop
    PLAYWRIGHT = "playwright"  # Playwright automation


@dataclass
class ScreenRegion:
    """A region of interest on the screen."""

    x: int
    y: int
    width: int
    height: int
    label: str = ""


@dataclass
class ComputerAction:
    """A single computer use action."""

    action_type: ActionType
    x: int | None = None
    y: int | None = None
    text: str | None = None
    key: str | None = None
    url: str | None = None
    scroll_direction: str | None = None
    scroll_amount: int = 3
    duration: float | None = None
    description: str = ""


@dataclass
class VisionObservation:
    """Observation from analyzing a screenshot."""

    description: str
    elements: list[ScreenRegion] = field(default_factory=list)
    suggested_action: ComputerAction | None = None
    confidence: float = 0.0
    raw_screenshot_b64: str = ""


@dataclass
class ComputerUseSession:
    """Manages a computer use session within a sandbox."""

    session_id: str
    sandbox_id: str
    backend: BrowserBackend = BrowserBackend.CDP
    viewport_width: int = 1280
    viewport_height: int = 800
    actions_taken: list[ComputerAction] = field(default_factory=list)
    screenshots: list[str] = field(default_factory=list)  # paths only
    max_screenshots_kept: int = 2
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    # Safety settings
    domain_whitelist: list[str] = field(
        default_factory=lambda: [
            "github.com",
            "stackoverflow.com",
            "docs.python.org",
            "developer.mozilla.org",
            "npmjs.com",
            "pypi.org",
        ]
    )
    max_actions_per_minute: int = 30
    stuck_detection_threshold: int = 3


class ComputerUseEngine:
    """Vision-loop engine for computer use within sandboxes.

    Cycle: screenshot -> multimodal LLM -> understand -> action -> screenshot

    Safety protections (from planning doc):
    - Domain whitelist
    - Sensitive area detection
    - Rate limiting
    - Stuck detection (3 same actions -> switch strategy)
    - Screenshot history compression (keep only last 2 full screenshots)
    """

    def __init__(self) -> None:
        self._sessions: dict[str, ComputerUseSession] = {}
        self._action_counts: dict[str, list[float]] = {}  # session_id -> timestamps

    def create_session(
        self,
        session_id: str,
        sandbox_id: str,
        backend: BrowserBackend = BrowserBackend.CDP,
        viewport: tuple[int, int] = (1280, 800),
    ) -> ComputerUseSession:
        """Create a new computer use session."""
        cu_session = ComputerUseSession(
            session_id=session_id,
            sandbox_id=sandbox_id,
            backend=backend,
            viewport_width=viewport[0],
            viewport_height=viewport[1],
        )
        self._sessions[session_id] = cu_session
        self._action_counts[session_id] = []
        return cu_session

    async def take_screenshot(self, session_id: str) -> str:
        """Capture screenshot from sandbox display.

        In production: uses CDP/VNC to capture actual screenshot.
        Returns base64-encoded PNG.
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Computer use session {session_id} not found")

        # Placeholder screenshot (1x1 white pixel PNG)
        placeholder = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4"
            "2mP8z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg=="
        )

        # Manage screenshot history (keep only last N)
        screenshot_id = f"screenshot_{uuid.uuid4().hex[:8]}"
        session.screenshots.append(screenshot_id)
        if len(session.screenshots) > session.max_screenshots_kept:
            session.screenshots = session.screenshots[-session.max_screenshots_kept :]

        return placeholder

    async def analyze_screenshot(
        self, session_id: str, screenshot_b64: str, task: str
    ) -> VisionObservation:
        """Analyze screenshot with multimodal LLM.

        In production: sends screenshot to GPT-4V/Claude Vision
        to understand what's on screen and suggest next action.
        """
        # Placeholder analysis
        return VisionObservation(
            description=f"Screenshot analyzed for task: {task}",
            elements=[],
            confidence=0.8,
        )

    async def execute_action(
        self, session_id: str, action: ComputerAction
    ) -> dict[str, Any]:
        """Execute a computer use action in the sandbox.

        In production: pipes action to CDP/Playwright/VNC client.
        """
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"Computer use session {session_id} not found")

        # Rate limiting
        if not self._check_rate_limit(session_id):
            return {
                "success": False,
                "error": "Rate limit exceeded (30 actions/minute)",
            }

        # Domain whitelist check for navigation
        if action.action_type == ActionType.NAVIGATE and action.url:
            if not self._check_domain(session, action.url):
                return {
                    "success": False,
                    "error": f"Domain not in whitelist: {action.url}",
                }

        # Stuck detection
        if self._detect_stuck(session, action):
            return {
                "success": False,
                "error": "Stuck detected (3 identical actions). Switch strategy.",
                "suggestion": "Try a different approach or element",
            }

        # Record action
        session.actions_taken.append(action)
        self._record_action_time(session_id)

        return {
            "success": True,
            "action": action.action_type.value,
            "description": action.description or f"Executed {action.action_type.value}",
        }

    async def vision_loop_step(
        self, session_id: str, task: str
    ) -> dict[str, Any]:
        """Execute one step of the vision loop.

        1. Take screenshot
        2. Analyze with multimodal LLM
        3. Execute suggested action
        4. Return result + new screenshot
        """
        # Step 1: Screenshot
        screenshot = await self.take_screenshot(session_id)

        # Step 2: Analyze
        observation = await self.analyze_screenshot(session_id, screenshot, task)

        # Step 3: Execute if action suggested
        result = {"observation": observation.description}
        if observation.suggested_action:
            exec_result = await self.execute_action(
                session_id, observation.suggested_action
            )
            result["action_result"] = exec_result

        return result

    def get_session(self, session_id: str) -> ComputerUseSession | None:
        return self._sessions.get(session_id)

    def close_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
        self._action_counts.pop(session_id, None)

    def _check_rate_limit(self, session_id: str) -> bool:
        """Check if actions per minute limit is exceeded."""
        import time

        now = time.time()
        timestamps = self._action_counts.get(session_id, [])
        # Keep only last 60 seconds
        timestamps = [t for t in timestamps if now - t < 60]
        self._action_counts[session_id] = timestamps
        return len(timestamps) < 30

    def _record_action_time(self, session_id: str) -> None:
        import time

        self._action_counts.setdefault(session_id, []).append(time.time())

    def _check_domain(self, session: ComputerUseSession, url: str) -> bool:
        """Check if URL domain is in whitelist."""
        from urllib.parse import urlparse

        try:
            domain = urlparse(url).netloc
            return any(w in domain for w in session.domain_whitelist)
        except Exception:
            return False

    def _detect_stuck(
        self, session: ComputerUseSession, action: ComputerAction
    ) -> bool:
        """Detect if Agent is stuck repeating the same action."""
        recent = session.actions_taken[-session.stuck_detection_threshold :]
        if len(recent) < session.stuck_detection_threshold:
            return False

        # Check if all recent actions are identical
        return all(
            a.action_type == action.action_type
            and a.x == action.x
            and a.y == action.y
            and a.text == action.text
            for a in recent
        )


# Singleton
computer_use_engine = ComputerUseEngine()
