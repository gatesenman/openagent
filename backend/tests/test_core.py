"""核心模块单元测试 / Core module unit tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_jwt_create_and_verify():
    from app.core.auth import Role, create_access_token, verify_token

    token = create_access_token(
        user_id="test-user",
        org_id="org-1",
        role=Role.ADMIN,
    )
    assert isinstance(token, str)
    parts = token.split(".")
    assert len(parts) == 3

    payload = verify_token(token)
    assert payload is not None
    assert payload.sub == "test-user"
    assert payload.org_id == "org-1"
    assert payload.role == Role.ADMIN


def test_jwt_expired():
    from app.core.auth import verify_token, create_access_token

    token = create_access_token("u1", expires_minutes=-1)
    assert verify_token(token) is None


def test_jwt_invalid():
    from app.core.auth import verify_token

    assert verify_token("invalid.token.here") is None
    assert verify_token("") is None


def test_user_store():
    from app.core.auth import UserStore, Role

    store = UserStore()
    user = store.create_user("alice", "alice@test.com", "pass123")
    assert user.username == "alice"

    authed = store.authenticate("alice", "pass123")
    assert authed is not None
    assert authed.id == user.id

    assert store.authenticate("alice", "wrong") is None
    assert store.authenticate("nobody", "pass") is None


def test_event_hub():
    import asyncio
    from app.core.event_hub import AgentEvent, EventType, EventHub

    hub = EventHub()

    async def _test():
        event = AgentEvent(
            type=EventType.AGENT_START,
            session_id="s1",
            data={"step": 1},
        )
        await hub.publish(event)
        history = hub.history("s1")
        assert len(history) == 1
        assert history[0].type == EventType.AGENT_START
        assert history[0].session_id == "s1"

    asyncio.run(_test())


def test_telemetry_metrics():
    from app.core.telemetry import MetricsCollector

    m = MetricsCollector()
    m.increment("test.count")
    m.increment("test.count")
    assert m.get_counter("test.count") == 2

    m.record("test.latency", 100.0)
    m.record("test.latency", 200.0)
    stats = m.get_histogram_stats("test.latency")
    assert stats["count"] == 2
    assert stats["mean"] == 150.0


def test_telemetry_tracer():
    from app.core.telemetry import Tracer

    t = Tracer()
    with t.start_span("test-op", attributes={"key": "val"}) as span:
        span.add_event("step1")

    traces = t.get_traces()
    assert len(traces) == 1
    assert traces[0]["name"] == "test-op"
    assert traces[0]["status"] == "ok"


def test_jsonrpc():
    from app.protocols.jsonrpc import JsonRpcRequest, JsonRpcResponse

    req = JsonRpcRequest.from_dict({
        "jsonrpc": "2.0",
        "method": "test",
        "params": {"a": 1},
        "id": "1",
    })
    assert req.method == "test"
    assert req.params["a"] == 1

    resp = JsonRpcResponse.success("1", {"result": "ok"})
    d = resp.to_dict()
    assert d["result"]["result"] == "ok"
    assert d["id"] == "1"
