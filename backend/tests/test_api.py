"""API 冒烟测试 / API smoke tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "OpenAgent"
    assert data["status"] == "running"


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_protocols_status(client):
    resp = client.get("/api/protocols")
    assert resp.status_code == 200
    protocols = resp.json()["protocols"]
    names = [p["name"] for p in protocols]
    assert "JSON-RPC 2.0" in names
    assert "MCP" in names
    assert "AG-UI" in names
    assert "A2A" in names


def test_mcp_info(client):
    resp = client.get("/mcp/info")
    assert resp.status_code == 200
    assert resp.json()["name"] == "openagent"


def test_agent_card(client):
    resp = client.get("/.well-known/agent.json")
    assert resp.status_code == 200
    card = resp.json()
    assert card["name"] == "OpenAgent"
    assert len(card["skills"]) > 0


def test_sessions_crud(client):
    # 创建
    resp = client.post(
        "/api/sessions/",
        json={"title": "测试会话", "mode": "localhost"},
    )
    assert resp.status_code == 200
    sid = resp.json()["id"]

    # 列表
    resp = client.get("/api/sessions/")
    assert resp.status_code == 200
    data = resp.json()
    assert any(s["id"] == sid for s in data["sessions"])

    # 获取
    resp = client.get(f"/api/sessions/{sid}")
    assert resp.status_code == 200
    assert resp.json()["title"] == "测试会话"


def test_auth_login(client):
    resp = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["username"] == "admin"


def test_auth_register(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@test.com",
            "password": "test123",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"


def test_knowledge_crud(client):
    # 创建
    resp = client.post(
        "/api/knowledge/",
        json={"name": "测试知识", "content": "测试内容", "layer": "user"},
    )
    assert resp.status_code == 200

    # 列表
    resp = client.get("/api/knowledge/")
    assert resp.status_code == 200


def test_playbooks_list(client):
    resp = client.get("/api/playbooks/")
    assert resp.status_code == 200
    playbooks = resp.json()
    assert len(playbooks) > 0


def test_deepwiki_endpoints(client):
    resp = client.get("/api/deepwiki/symbols?repo_path=.")
    assert resp.status_code == 200


def test_codemaps_endpoints(client):
    resp = client.get("/api/codemaps/")
    assert resp.status_code == 200


def test_tools_list(client):
    resp = client.get("/api/tools/")
    assert resp.status_code == 200
    tools = resp.json()
    assert len(tools) > 0


def test_analytics_metrics(client):
    resp = client.get("/api/analytics/metrics")
    assert resp.status_code == 200
    data = resp.json()
    assert "counters" in data


def test_analytics_overview(client):
    resp = client.get("/api/analytics/overview")
    assert resp.status_code == 200
    data = resp.json()
    assert "llm" in data
    assert "tools" in data


def test_events_worklog(client):
    resp = client.get("/api/events/test-session/worklog")
    assert resp.status_code == 200
    assert resp.json()["session_id"] == "test-session"
