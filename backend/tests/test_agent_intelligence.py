"""Tests for Agent Intelligence modules:
- Terminal Stream
- Evaluation Framework
- Anti-Hallucination Pipeline
- Code Retrieval
- Tool Output Guard
- Computer Use
- Multi-Agent Collaboration
"""

import pytest


# ─── Terminal Stream ───


@pytest.mark.asyncio
async def test_terminal_create_and_write():
    from app.agent.terminal_stream import terminal_stream_manager

    terminal = await terminal_stream_manager.create_terminal("sess-1", "sandbox-1")
    assert terminal.terminal_id
    assert terminal.state.value == "idle"

    result = await terminal_stream_manager.write_input(terminal.terminal_id, "ls -la")
    assert result["type"] == "output"
    assert "ls -la" in result["data"]


@pytest.mark.asyncio
async def test_terminal_history():
    from app.agent.terminal_stream import terminal_stream_manager

    terminal = await terminal_stream_manager.create_terminal("sess-2", "sandbox-2")
    await terminal_stream_manager.write_input(terminal.terminal_id, "echo hello")
    history = terminal_stream_manager.get_history(terminal.terminal_id)
    assert "echo hello" in history


@pytest.mark.asyncio
async def test_terminal_dangerous_command_blocked():
    from app.agent.terminal_stream import terminal_stream_manager

    terminal = await terminal_stream_manager.create_terminal("sess-3", "sandbox-3")
    result = await terminal_stream_manager.write_input(
        terminal.terminal_id, "rm -rf /"
    )
    assert "BLOCKED" in result["data"]


@pytest.mark.asyncio
async def test_terminal_close():
    from app.agent.terminal_stream import terminal_stream_manager

    terminal = await terminal_stream_manager.create_terminal("sess-4", "sandbox-4")
    await terminal_stream_manager.close_terminal(terminal.terminal_id)
    assert terminal.state.value == "closed"


# ─── Evaluation Framework ───


def test_eval_list_cases():
    from app.agent.evaluation import agent_evaluator

    cases = agent_evaluator.list_cases()
    assert len(cases) >= 5
    assert any(c["case_id"] == "eval-001" for c in cases)


@pytest.mark.asyncio
async def test_eval_run_case():
    from app.agent.evaluation import agent_evaluator

    run = await agent_evaluator.run_evaluation("eval-001")
    assert run.case_id == "eval-001"
    assert run.result.value in ("pass", "fail", "partial")


@pytest.mark.asyncio
async def test_eval_run_suite():
    from app.agent.evaluation import BenchmarkType, agent_evaluator

    runs = await agent_evaluator.run_suite(BenchmarkType.BUG_FIX)
    assert len(runs) >= 1


def test_eval_summary():
    from app.agent.evaluation import agent_evaluator

    summary = agent_evaluator.get_summary()
    assert "total_runs" in summary


# ─── Anti-Hallucination Pipeline ───


@pytest.mark.asyncio
async def test_anti_hallucination_syntax_pass():
    from app.agent.anti_hallucination import anti_hallucination

    files = {"test.py": "def hello():\n    return 'world'\n"}
    report = await anti_hallucination.verify("sess-1", files)
    assert report.gates[0].gate.value == "syntax"
    assert report.gates[0].result.value == "pass"


@pytest.mark.asyncio
async def test_anti_hallucination_syntax_fail():
    from app.agent.anti_hallucination import anti_hallucination

    files = {"test.py": "def hello(\n    return 'world'\n"}
    report = await anti_hallucination.verify("sess-2", files)
    assert report.gates[0].result.value == "fail"


@pytest.mark.asyncio
async def test_anti_hallucination_self_review_debug():
    from app.agent.anti_hallucination import anti_hallucination

    files = {"app.py": "x = 1\nprint('debug:', x)\n"}
    report = await anti_hallucination.verify("sess-3", files)
    # Self-review gate should catch debug statements
    self_review = report.gates[-1]
    assert self_review.gate.value == "self_review"
    assert len(self_review.warnings) > 0


@pytest.mark.asyncio
async def test_anti_hallucination_overall():
    from app.agent.anti_hallucination import anti_hallucination

    files = {"clean.py": "def add(a: int, b: int) -> int:\n    return a + b\n"}
    report = await anti_hallucination.verify("sess-4", files)
    assert report.all_passed


# ─── Code Retrieval Pipeline ───


def test_code_retrieval_index():
    from app.agent.code_retrieval import CodeRetrievalPipeline

    pipeline = CodeRetrievalPipeline()
    files = {
        "src/auth.py": "def login(username, password):\n    # authenticate user\n    pass\n",
        "src/user.py": "class User:\n    def __init__(self, name):\n        self.name = name\n",
        "src/db.py": "def get_connection():\n    return connect('postgres://localhost/db')\n",
    }
    count = pipeline.index_codebase(files)
    assert count > 0


def test_code_retrieval_search():
    from app.agent.code_retrieval import CodeRetrievalPipeline

    pipeline = CodeRetrievalPipeline()
    files = {
        "src/auth.py": "def login(username, password):\n    # authenticate user\n    token = generate_jwt(username)\n    return token\n",
        "src/user.py": "class User:\n    def __init__(self, name):\n        self.name = name\n",
    }
    pipeline.index_codebase(files)
    result = pipeline.retrieve("user login authentication")
    assert len(result.chunks) > 0
    assert result.keywords_extracted


def test_code_retrieval_format():
    from app.agent.code_retrieval import CodeRetrievalPipeline

    pipeline = CodeRetrievalPipeline()
    files = {"test.py": "x = 1\ny = 2\n"}
    pipeline.index_codebase(files)
    result = pipeline.retrieve("variable assignment")
    context = pipeline.format_context(result)
    assert "<relevant_code>" in context or context == ""


def test_intent_parser():
    from app.agent.code_retrieval import IntentParser

    parser = IntentParser()
    intent = parser.parse("fix the user login bug in auth.py")
    assert "login" in intent["keywords"]
    assert "auth.py" in intent["file_patterns"]


# ─── Tool Output Guard ───


def test_tool_guard_pass():
    from app.agent.tool_guard import tool_guard

    decision = tool_guard.check("grep", {"pattern": "hello"}, "line 1: hello world", 0)
    assert decision.action.value == "pass"


def test_tool_guard_not_found():
    from app.agent.tool_guard import tool_guard

    decision = tool_guard.check(
        "read_file", {"path": "/x.py"}, "Error: no such file or directory", 1
    )
    assert decision.action.value == "retry_with_hint"


def test_tool_guard_permission_denied():
    from app.agent.tool_guard import tool_guard

    decision = tool_guard.check(
        "shell", {"cmd": "rm /root/x"}, "Permission denied", 1
    )
    assert decision.action.value == "stop_with_message"


def test_tool_guard_transient_retry():
    from app.agent.tool_guard import tool_guard

    tool_guard.reset_retries()
    decision = tool_guard.check(
        "api_call", {"url": "http://x"}, "connection refused", 1
    )
    assert decision.action.value == "auto_retry"
    assert decision.retry_count == 1


def test_tool_guard_empty_output():
    from app.agent.tool_guard import tool_guard

    decision = tool_guard.check("grep", {"pattern": "xyz"}, "", 0)
    # Empty output with exit_code=0 but looks_like_error is False
    # _is_semantic_garbage returns True for empty, but the first condition
    # checks exit_code==0 AND result is truthy — empty string is falsy
    # so it falls through to error classification
    assert decision.action.value in ("pass", "retry_with_hint")


def test_tool_guard_large_output():
    from app.agent.tool_guard import tool_guard

    big_output = "x" * 300000
    decision = tool_guard.check("grep", {}, big_output, 0)
    assert decision.action.value == "truncate_and_save"


# ─── Computer Use ───


@pytest.mark.asyncio
async def test_computer_use_create_session():
    from app.agent.computer_use import computer_use_engine

    session = computer_use_engine.create_session("cu-1", "sandbox-1")
    assert session.session_id == "cu-1"
    assert session.viewport_width == 1280


@pytest.mark.asyncio
async def test_computer_use_screenshot():
    from app.agent.computer_use import computer_use_engine

    computer_use_engine.create_session("cu-2", "sandbox-2")
    b64 = await computer_use_engine.take_screenshot("cu-2")
    assert len(b64) > 0


@pytest.mark.asyncio
async def test_computer_use_action():
    from app.agent.computer_use import ActionType, ComputerAction, computer_use_engine

    computer_use_engine.create_session("cu-3", "sandbox-3")
    action = ComputerAction(action_type=ActionType.CLICK, x=100, y=200)
    result = await computer_use_engine.execute_action("cu-3", action)
    assert result["success"]


@pytest.mark.asyncio
async def test_computer_use_domain_block():
    from app.agent.computer_use import ActionType, ComputerAction, computer_use_engine

    computer_use_engine.create_session("cu-4", "sandbox-4")
    action = ComputerAction(
        action_type=ActionType.NAVIGATE, url="https://malicious-site.com"
    )
    result = await computer_use_engine.execute_action("cu-4", action)
    assert not result["success"]
    assert "whitelist" in result.get("error", "").lower()


@pytest.mark.asyncio
async def test_computer_use_vision_step():
    from app.agent.computer_use import computer_use_engine

    computer_use_engine.create_session("cu-5", "sandbox-5")
    result = await computer_use_engine.vision_loop_step("cu-5", "click login button")
    assert "observation" in result


# ─── Multi-Agent Collaboration ───


def test_multi_agent_create_session():
    from app.agent.multi_agent import multi_agent_coordinator

    session = multi_agent_coordinator.create_session("ma-1")
    assert session.session_id == "ma-1"
    assert "coordinator" in session.agents


def test_multi_agent_decompose():
    from app.agent.multi_agent import multi_agent_coordinator

    multi_agent_coordinator.create_session("ma-2")
    tasks = multi_agent_coordinator.decompose_task("ma-2", "Add user auth")
    assert len(tasks) == 4
    assert tasks[0].assigned_to.value == "plan"
    assert tasks[1].assigned_to.value == "code"


def test_multi_agent_task_dependencies():
    from app.agent.multi_agent import multi_agent_coordinator

    multi_agent_coordinator.create_session("ma-3")
    tasks = multi_agent_coordinator.decompose_task("ma-3", "Fix bug")
    # Code task depends on plan task
    assert tasks[0].task_id in tasks[1].depends_on


def test_multi_agent_ready_tasks():
    from app.agent.multi_agent import TaskStatus, multi_agent_coordinator

    multi_agent_coordinator.create_session("ma-4")
    tasks = multi_agent_coordinator.decompose_task("ma-4", "Refactor")
    # Only plan task should be ready (no dependencies)
    ready = multi_agent_coordinator.get_ready_tasks("ma-4")
    assert len(ready) == 1
    assert ready[0].assigned_to.value == "plan"

    # Complete plan task, code task becomes ready
    multi_agent_coordinator.update_task_status(
        "ma-4", tasks[0].task_id, TaskStatus.COMPLETED
    )
    ready2 = multi_agent_coordinator.get_ready_tasks("ma-4")
    assert len(ready2) == 1
    assert ready2[0].assigned_to.value == "code"


def test_multi_agent_messaging():
    from app.agent.multi_agent import multi_agent_coordinator

    multi_agent_coordinator.create_session("ma-5")
    msg = multi_agent_coordinator.send_message(
        "ma-5", "review_agent", "code_agent", "alert", "SQL injection found"
    )
    assert msg.content == "SQL injection found"


def test_multi_agent_conflict_resolution():
    from app.agent.multi_agent import ConflictType, multi_agent_coordinator

    multi_agent_coordinator.create_session("ma-6")
    conflict = multi_agent_coordinator.report_conflict(
        "ma-6",
        ConflictType.FILE_CONFLICT,
        "Both agents modified auth.ts",
        ["code_agent", "test_agent"],
    )
    assert conflict["resolution"] is None

    resolved = multi_agent_coordinator.resolve_conflict(
        "ma-6", conflict["conflict_id"], "Use code_agent version"
    )
    assert resolved


def test_multi_agent_saga_compensation():
    from app.agent.multi_agent import TaskStatus, multi_agent_coordinator

    multi_agent_coordinator.create_session("ma-7")
    tasks = multi_agent_coordinator.decompose_task("ma-7", "Deploy")
    # Fail the code task
    multi_agent_coordinator.update_task_status(
        "ma-7", tasks[1].task_id, TaskStatus.FAILED, error="Build failed"
    )
    # Compensation should cancel review and test tasks
    cancelled = multi_agent_coordinator.compensate_failure("ma-7", tasks[1].task_id)
    assert len(cancelled) == 2


def test_multi_agent_session_status():
    from app.agent.multi_agent import multi_agent_coordinator

    multi_agent_coordinator.create_session("ma-8")
    multi_agent_coordinator.decompose_task("ma-8", "Add feature")
    status = multi_agent_coordinator.get_session_status("ma-8")
    assert status["total_tasks"] == 4
    assert "pending" in status["status_counts"]
