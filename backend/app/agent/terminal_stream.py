"""WebSocket Terminal Stream — real-time sandbox shell interaction.

Provides bidirectional WebSocket connection for terminal I/O
between the frontend terminal panel and the sandbox shell.
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class TerminalState(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    CLOSED = "closed"


@dataclass
class TerminalBuffer:
    """Ring buffer for terminal output history."""

    max_lines: int = 5000
    lines: list[str] = field(default_factory=list)

    def append(self, data: str) -> None:
        new_lines = data.split("\n")
        self.lines.extend(new_lines)
        if len(self.lines) > self.max_lines:
            self.lines = self.lines[-self.max_lines :]

    def get_history(self, last_n: int = 100) -> str:
        return "\n".join(self.lines[-last_n:])


@dataclass
class TerminalSession:
    """Manages a single terminal session within a sandbox."""

    session_id: str
    sandbox_id: str
    terminal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    state: TerminalState = TerminalState.IDLE
    buffer: TerminalBuffer = field(default_factory=TerminalBuffer)
    cwd: str = "/workspace"
    env: dict[str, str] = field(default_factory=dict)
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    shell: str = "/bin/bash"
    cols: int = 120
    rows: int = 40


class TerminalStreamManager:
    """Manages WebSocket terminal streams for sandbox interaction.

    Each session can have multiple terminal tabs, each connected
    to the same sandbox but with independent shell processes.
    """

    def __init__(self) -> None:
        self._terminals: dict[str, TerminalSession] = {}
        self._subscribers: dict[str, list[asyncio.Queue]] = {}
        self._command_history: dict[str, list[dict[str, Any]]] = {}

    async def create_terminal(
        self,
        session_id: str,
        sandbox_id: str,
        shell: str = "/bin/bash",
        cols: int = 120,
        rows: int = 40,
    ) -> TerminalSession:
        """Create a new terminal session attached to a sandbox."""
        terminal = TerminalSession(
            session_id=session_id,
            sandbox_id=sandbox_id,
            shell=shell,
            cols=cols,
            rows=rows,
        )
        self._terminals[terminal.terminal_id] = terminal
        self._subscribers[terminal.terminal_id] = []
        self._command_history[terminal.terminal_id] = []
        return terminal

    async def write_input(self, terminal_id: str, data: str) -> dict[str, Any]:
        """Send input to the terminal (user typing or Agent commands)."""
        terminal = self._terminals.get(terminal_id)
        if not terminal:
            raise ValueError(f"Terminal {terminal_id} not found")

        terminal.state = TerminalState.RUNNING

        # Record command
        entry = {
            "type": "input",
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._command_history[terminal_id].append(entry)

        # Simulate sandbox execution (in production: pipe to sandbox PTY)
        output = await self._execute_in_sandbox(terminal, data)

        # Record output
        out_entry = {
            "type": "output",
            "data": output,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._command_history[terminal_id].append(out_entry)

        terminal.buffer.append(output)
        terminal.state = TerminalState.IDLE

        # Broadcast to subscribers
        await self._broadcast(terminal_id, out_entry)

        return out_entry

    async def subscribe(self, terminal_id: str) -> asyncio.Queue:
        """Subscribe to terminal output events."""
        if terminal_id not in self._subscribers:
            raise ValueError(f"Terminal {terminal_id} not found")
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers[terminal_id].append(queue)
        return queue

    def unsubscribe(self, terminal_id: str, queue: asyncio.Queue) -> None:
        """Unsubscribe from terminal output events."""
        if terminal_id in self._subscribers:
            try:
                self._subscribers[terminal_id].remove(queue)
            except ValueError:
                pass

    async def resize(self, terminal_id: str, cols: int, rows: int) -> None:
        """Resize terminal dimensions."""
        terminal = self._terminals.get(terminal_id)
        if terminal:
            terminal.cols = cols
            terminal.rows = rows

    def get_history(self, terminal_id: str, last_n: int = 100) -> str:
        """Get terminal output history."""
        terminal = self._terminals.get(terminal_id)
        if not terminal:
            return ""
        return terminal.buffer.get_history(last_n)

    def get_command_history(self, terminal_id: str) -> list[dict[str, Any]]:
        """Get command input/output history."""
        return self._command_history.get(terminal_id, [])

    async def close_terminal(self, terminal_id: str) -> None:
        """Close a terminal session."""
        terminal = self._terminals.get(terminal_id)
        if terminal:
            terminal.state = TerminalState.CLOSED
            # Notify subscribers
            await self._broadcast(
                terminal_id, {"type": "close", "terminal_id": terminal_id}
            )
            self._terminals.pop(terminal_id, None)
            self._subscribers.pop(terminal_id, None)

    async def _execute_in_sandbox(
        self, terminal: TerminalSession, command: str
    ) -> str:
        """Execute command in the sandbox environment.

        In production this pipes to the Docker/VM PTY.
        For now returns a structured response.
        """
        # Shell-dangerous command detection
        dangerous = ["rm -rf /", ":(){ :|:& };:", "mkfs", "dd if=/dev/zero"]
        for d in dangerous:
            if d in command:
                return f"[BLOCKED] Dangerous command detected: {command}"

        return f"$ {command}\n[sandbox:{terminal.sandbox_id}] Executed in {terminal.cwd}"

    async def _broadcast(
        self, terminal_id: str, message: dict[str, Any]
    ) -> None:
        """Broadcast message to all subscribers of a terminal."""
        for queue in self._subscribers.get(terminal_id, []):
            await queue.put(message)


# Singleton
terminal_stream_manager = TerminalStreamManager()
