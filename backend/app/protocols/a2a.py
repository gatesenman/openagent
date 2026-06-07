"""A2A 协议 / Agent-to-Agent Protocol.

实现 Agent 间协作的标准协议骨架。
参考: https://google.github.io/A2A/

核心概念:
- Agent Card: Agent 能力声明（类似 DNS SRV 记录）
- Task: Agent 间协作的任务单元
- Message/Part: 任务中的消息和内容块
"""

import time
import uuid
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class TaskState(str, Enum):
    """A2A 任务状态."""

    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    CANCELED = "canceled"
    FAILED = "failed"


@dataclass
class AgentSkill:
    """Agent 技能声明."""

    id: str
    name: str
    description: str
    tags: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "examples": self.examples,
        }


@dataclass
class AgentCard:
    """Agent Card — Agent 能力声明.

    每个 Agent 通过 /.well-known/agent.json 暴露自己的能力。
    其他 Agent 通过读取 Agent Card 来发现和选择协作伙伴。
    """

    name: str
    description: str
    url: str
    version: str = "0.1.0"
    protocol_version: str = "0.2.2"
    skills: list[AgentSkill] = field(default_factory=list)
    capabilities: dict[str, bool] = field(default_factory=lambda: {
        "streaming": True,
        "pushNotifications": False,
        "stateTransitionHistory": True,
    })
    authentication: dict[str, Any] = field(default_factory=lambda: {
        "schemes": ["bearer"],
    })
    default_input_modes: list[str] = field(
        default_factory=lambda: ["text"]
    )
    default_output_modes: list[str] = field(
        default_factory=lambda: ["text"]
    )

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "url": self.url,
            "version": self.version,
            "protocolVersion": self.protocol_version,
            "skills": [s.to_dict() for s in self.skills],
            "capabilities": self.capabilities,
            "authentication": self.authentication,
            "defaultInputModes": self.default_input_modes,
            "defaultOutputModes": self.default_output_modes,
        }


@dataclass
class TaskPart:
    """任务消息中的内容块."""

    type: str = "text"  # text / file / data
    text: str = ""
    file_uri: str = ""
    mime_type: str = ""
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        result: dict[str, Any] = {"type": self.type}
        if self.text:
            result["text"] = self.text
        if self.file_uri:
            result["file"] = {
                "uri": self.file_uri,
                "mimeType": self.mime_type,
            }
        if self.metadata:
            result["metadata"] = self.metadata
        return result


@dataclass
class TaskMessage:
    """任务消息."""

    role: str  # "user" / "agent"
    parts: list[TaskPart] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "role": self.role,
            "parts": [p.to_dict() for p in self.parts],
            "metadata": self.metadata,
        }


@dataclass
class TaskStatus:
    """任务状态."""

    state: TaskState
    message: TaskMessage | None = None
    timestamp: str = field(
        default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    )

    def to_dict(self) -> dict:
        result: dict[str, Any] = {
            "state": self.state.value,
            "timestamp": self.timestamp,
        }
        if self.message:
            result["message"] = self.message.to_dict()
        return result


@dataclass
class Task:
    """A2A 任务.

    Agent 间协作的基本单元。
    支持状态转换: submitted → working → completed/failed
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    status: TaskStatus = field(
        default_factory=lambda: TaskStatus(state=TaskState.SUBMITTED)
    )
    history: list[TaskMessage] = field(default_factory=list)
    artifacts: list[dict] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sessionId": self.session_id,
            "status": self.status.to_dict(),
            "history": [m.to_dict() for m in self.history],
            "artifacts": self.artifacts,
            "metadata": self.metadata,
        }


class A2AServer:
    """A2A Server — 接收其他 Agent 的协作请求.

    标准方法 (JSON-RPC):
    - tasks/send: 接收任务
    - tasks/get: 查询任务状态
    - tasks/cancel: 取消任务
    - tasks/sendSubscribe: 订阅任务更新（SSE）
    """

    def __init__(self, agent_card: AgentCard):
        self.agent_card = agent_card
        self._tasks: dict[str, Task] = {}

    async def handle_send(self, params: dict) -> dict:
        """处理 tasks/send 请求."""
        task_id = params.get("id", str(uuid.uuid4()))
        session_id = params.get("sessionId", "")

        message_data = params.get("message", {})
        parts = [
            TaskPart(
                type=p.get("type", "text"),
                text=p.get("text", ""),
            )
            for p in message_data.get("parts", [])
        ]
        message = TaskMessage(
            role=message_data.get("role", "user"),
            parts=parts,
        )

        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.history.append(message)
        else:
            task = Task(
                id=task_id,
                session_id=session_id,
                history=[message],
            )
            self._tasks[task_id] = task

        # 标记为工作中
        task.status = TaskStatus(state=TaskState.WORKING)
        logger.info("A2A 任务接收: id=%s", task_id)

        return task.to_dict()

    async def handle_get(self, params: dict) -> dict:
        """查询任务状态."""
        task_id = params.get("id", "")
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"任务不存在: {task_id}")
        return task.to_dict()

    async def handle_cancel(self, params: dict) -> dict:
        """取消任务."""
        task_id = params.get("id", "")
        task = self._tasks.get(task_id)
        if not task:
            raise ValueError(f"任务不存在: {task_id}")
        task.status = TaskStatus(state=TaskState.CANCELED)
        return task.to_dict()

    def get_agent_card(self) -> dict:
        """返回 Agent Card."""
        return self.agent_card.to_dict()


class A2AClient:
    """A2A Client — 向其他 Agent 发送协作请求.

    通过 HTTP/JSON-RPC 与远程 Agent 通信。
    """

    def __init__(self):
        self._agents: dict[str, AgentCard] = {}

    async def discover(self, url: str) -> AgentCard:
        """发现远程 Agent.

        读取 {url}/.well-known/agent.json 获取 Agent Card。
        """
        logger.info("A2A 发现: %s", url)
        # 实际实现中通过 HTTP GET 获取
        card = AgentCard(
            name="remote-agent",
            description="远程 Agent",
            url=url,
        )
        self._agents[url] = card
        return card

    async def send_task(
        self, agent_url: str, message: str, task_id: str = ""
    ) -> dict:
        """向远程 Agent 发送任务."""
        logger.info("A2A 发送任务: agent=%s", agent_url)
        # 实际实现中通过 HTTP POST 发送 JSON-RPC 请求
        return {
            "id": task_id or str(uuid.uuid4()),
            "status": {"state": "submitted"},
        }

    def list_agents(self) -> list[dict]:
        """列出已发现的 Agent."""
        return [card.to_dict() for card in self._agents.values()]


# 全局实例
openagent_card = AgentCard(
    name="OpenAgent",
    description="AI 驱动的全生命周期软件开发平台",
    url="http://localhost:8000",
    skills=[
        AgentSkill(
            id="code-generation",
            name="代码生成",
            description="根据需求在沙箱中生成代码",
            tags=["coding", "development"],
        ),
        AgentSkill(
            id="code-review",
            name="代码审查",
            description="分析代码质量并提供改进建议",
            tags=["review", "quality"],
        ),
        AgentSkill(
            id="testing",
            name="自动测试",
            description="在沙箱中编写和运行测试",
            tags=["testing", "qa"],
        ),
        AgentSkill(
            id="deepwiki",
            name="代码文档生成",
            description="符号级自动文档生成(DeepWiki)",
            tags=["documentation", "wiki"],
        ),
        AgentSkill(
            id="codemap",
            name="代码结构分析",
            description="代码结构可视化和度量(CodeMap)",
            tags=["analysis", "visualization"],
        ),
    ],
)
a2a_server = A2AServer(openagent_card)
a2a_client = A2AClient()
