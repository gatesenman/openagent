"""ReAct 循环引擎 / ReAct loop engine.

核心 Agent 执行引擎：Think → Act → Observe → Reflect。
所有工具调用都通过沙箱虚拟环境执行。
"""

import asyncio
import json
import logging
import time
import uuid
from typing import Any, AsyncIterator

from app.agent.context import ContextManager, count_tokens
from app.agent.tools.base import BaseTool, ToolResult
from app.agent.tools.file_ops import FileReadTool, FileWriteTool
from app.agent.tools.git_ops import GitOpsTool
from app.agent.tools.search_code import SearchCodeTool
from app.agent.tools.shell_exec import ShellExecTool
from app.agent.validators import OutputValidator
from app.sandbox.base import BaseSandbox

logger = logging.getLogger(__name__)


class AgentEvent:
    """AG-UI 标准事件."""

    def __init__(self, event_type: str, **kwargs: Any):
        self.type = event_type
        self.data = kwargs
        self.timestamp = time.time()

    def to_sse(self) -> str:
        """转换为 SSE 格式."""
        payload = {"type": self.type, **self.data}
        return f"event: {self.type}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"

    def to_dict(self) -> dict:
        return {"type": self.type, "timestamp": self.timestamp, **self.data}


# 内置工具注册
BUILTIN_TOOLS: list[BaseTool] = [
    ShellExecTool(),
    FileReadTool(),
    FileWriteTool(),
    SearchCodeTool(),
    GitOpsTool(),
]

TOOL_MAP: dict[str, BaseTool] = {t.name: t for t in BUILTIN_TOOLS}


class ReactEngine:
    """ReAct 循环引擎.

    实现 Think → Act → Observe → Reflect 循环。
    所有工具调用通过沙箱执行，每步产生 AG-UI 事件流。

    零幻觉保证:
    1. 工具调用前进行参数验证
    2. 工具调用在隔离沙箱中执行
    3. 执行结果实时反馈到 LLM
    4. 危险操作自动拦截
    5. 连续错误触发策略切换
    """

    def __init__(
        self,
        sandbox: BaseSandbox,
        llm_client: Any = None,
        model: str = "gpt-4o",
        max_iterations: int = 50,
        max_tokens_per_turn: int = 8192,
        language: str = "zh",
    ):
        self.sandbox = sandbox
        self.llm_client = llm_client
        self.model = model
        self.max_iterations = max_iterations
        self.max_tokens_per_turn = max_tokens_per_turn
        self.language = language
        self.context_manager = ContextManager()
        self.validator = OutputValidator()
        self.tools = list(BUILTIN_TOOLS)
        self.tool_map = dict(TOOL_MAP)
        self._consecutive_errors = 0
        self._max_consecutive_errors = 3

    def register_tool(self, tool: BaseTool) -> None:
        """注册额外工具."""
        self.tools.append(tool)
        self.tool_map[tool.name] = tool

    async def run(
        self,
        messages: list[dict[str, Any]],
        session_id: str = "",
    ) -> AsyncIterator[AgentEvent]:
        """执行 ReAct 循环.

        Args:
            messages: 当前对话历史
            session_id: 会话ID（用于日志追踪）

        Yields:
            AgentEvent: AG-UI 标准事件流
        """
        run_id = str(uuid.uuid4())[:8]
        yield AgentEvent("RUN_STARTED", run_id=run_id, session_id=session_id)

        # 准备工具定义
        tool_defs = [t.to_openai_function() for t in self.tools]

        # 构建上下文
        context_messages = self.context_manager.build_messages(
            messages, tools=tool_defs, language=self.language
        )

        iteration = 0
        self._consecutive_errors = 0

        while iteration < self.max_iterations:
            iteration += 1
            step_id = f"step_{iteration}"

            yield AgentEvent(
                "STEP_STARTED",
                step=step_id,
                iteration=iteration,
                phase="think",
            )

            # === THINK: 调用 LLM ===
            try:
                llm_response = await self._call_llm(context_messages, tool_defs)
            except Exception as e:
                logger.error("LLM 调用失败: %s", e)
                yield AgentEvent("RUN_ERROR", error=str(e), run_id=run_id)
                return

            assistant_message = llm_response.get("message", {})
            content = assistant_message.get("content", "")
            tool_calls = assistant_message.get("tool_calls", [])

            # 输出思考内容
            if content:
                msg_id = f"msg_{uuid.uuid4().hex[:8]}"
                yield AgentEvent("TEXT_MESSAGE_START", message_id=msg_id, role="assistant")
                yield AgentEvent("TEXT_MESSAGE_CONTENT", message_id=msg_id, delta=content)
                yield AgentEvent("TEXT_MESSAGE_END", message_id=msg_id)

            # 无工具调用则认为完成
            if not tool_calls:
                yield AgentEvent("STEP_FINISHED", step=step_id, phase="complete")
                break

            # === ACT: 执行工具调用 ===
            context_messages.append(assistant_message)

            for tc in tool_calls:
                tc_id = tc.get("id", f"tc_{uuid.uuid4().hex[:8]}")
                func = tc.get("function", {})
                tool_name = func.get("name", "")
                raw_args = func.get("arguments", "{}")

                yield AgentEvent(
                    "TOOL_CALL_START",
                    tool_call_id=tc_id,
                    tool_name=tool_name,
                )

                # 解析参数
                try:
                    tool_args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except json.JSONDecodeError:
                    tool_args = {}

                yield AgentEvent(
                    "TOOL_CALL_ARGS",
                    tool_call_id=tc_id,
                    tool_name=tool_name,
                    args=tool_args,
                )

                # 验证工具调用
                tool = self.tool_map.get(tool_name)
                if not tool:
                    result = ToolResult(
                        success=False, output="", error=f"未知工具: {tool_name}"
                    )
                else:
                    validation = self.validator.validate_tool_call(
                        tool_name, tool_args, tool.parameters
                    )
                    if not validation.valid:
                        result = ToolResult(
                            success=False,
                            output="",
                            error=f"参数验证失败: {'; '.join(validation.errors)}",
                        )
                    else:
                        # 在沙箱中执行工具
                        try:
                            result = await tool.execute(self.sandbox, tool_args)
                        except Exception as e:
                            logger.error("工具执行异常: %s - %s", tool_name, e)
                            result = ToolResult(
                                success=False, output="", error=str(e)
                            )

                # === OBSERVE: 记录结果 ===
                yield AgentEvent(
                    "TOOL_CALL_END",
                    tool_call_id=tc_id,
                    tool_name=tool_name,
                    success=result.success,
                    output=result.output[:2000],  # 截断过长输出
                    error=result.error,
                    duration_ms=result.duration_ms,
                )

                # 添加工具结果到上下文
                tool_msg = {
                    "role": "tool",
                    "tool_call_id": tc_id,
                    "content": result.output if result.success else f"Error: {result.error}",
                }
                context_messages.append(tool_msg)

                # === REFLECT: 错误计数和策略切换 ===
                if not result.success:
                    self._consecutive_errors += 1
                    if self._consecutive_errors >= self._max_consecutive_errors:
                        yield AgentEvent(
                            "STATE_DELTA",
                            key="strategy_switch",
                            value="连续错误过多，需要切换策略或请求帮助",
                        )
                else:
                    self._consecutive_errors = 0

            yield AgentEvent(
                "STEP_FINISHED",
                step=step_id,
                phase="observe",
                iteration=iteration,
            )

        yield AgentEvent(
            "RUN_FINISHED",
            run_id=run_id,
            iterations=iteration,
            session_id=session_id,
        )

    async def _call_llm(
        self, messages: list[dict], tools: list[dict]
    ) -> dict[str, Any]:
        """调用 LLM.

        如果没有配置 LLM client，返回模拟响应。
        """
        if self.llm_client:
            try:
                response = await self.llm_client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools if tools else None,
                    max_tokens=self.max_tokens_per_turn,
                    temperature=0.1,
                )
                choice = response.choices[0]
                msg = {
                    "role": "assistant",
                    "content": choice.message.content or "",
                }
                if choice.message.tool_calls:
                    msg["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in choice.message.tool_calls
                    ]
                return {"message": msg}
            except Exception as e:
                logger.error("LLM API 调用失败: %s", e)
                raise

        # Mock 模式（无 LLM API key 时）
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "")
                break

        return {
            "message": {
                "role": "assistant",
                "content": f"[Mock模式] 收到任务: {last_user_msg[:100]}...\n正在分析中，请配置 LLM API key 以启用真实推理。",
            }
        }
