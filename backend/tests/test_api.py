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


# --- 新增模块测试 ---

def test_automations_rules(client):
    """自动化规则列表."""
    resp = client.get("/api/automations/rules")
    assert resp.status_code == 200
    rules = resp.json()
    assert isinstance(rules, list)
    assert len(rules) >= 2  # 2个默认规则


def test_automations_create_rule(client):
    """创建自动化规则."""
    resp = client.post("/api/automations/rules", json={
        "name": "测试规则",
        "description": "自动化测试",
        "trigger_type": "webhook",
    })
    assert resp.status_code == 200
    assert resp.json()["name"] == "测试规则"


def test_automations_schedules(client):
    """定时任务列表."""
    resp = client.get("/api/automations/schedules")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_automations_webhook(client):
    """Webhook 接收."""
    resp = client.post("/api/automations/webhook", json={
        "event_type": "push",
        "payload": {"ref": "refs/heads/main"},
    })
    assert resp.status_code == 200
    assert resp.json()["event_type"] == "push"


def test_mcp_marketplace_servers(client):
    """MCP 工具市场 - 服务器列表."""
    resp = client.get("/api/mcp/marketplace/servers")
    assert resp.status_code == 200
    servers = resp.json()
    assert isinstance(servers, list)
    assert len(servers) >= 4  # 至少4个内置


def test_mcp_marketplace_install(client):
    """MCP 工具市场 - 安装服务器."""
    resp = client.post("/api/mcp/marketplace/servers/github/install")
    assert resp.status_code == 200
    assert resp.json()["installed"] is True


def test_mcp_marketplace_tools(client):
    """MCP 工具市场 - 工具列表."""
    resp = client.get("/api/mcp/marketplace/tools")
    assert resp.status_code == 200
    tools = resp.json()
    assert isinstance(tools, list)
    assert len(tools) >= 5  # 内置工具


def test_session_lifecycle_pause_resume(client):
    """会话生命周期 - 暂停/恢复."""
    # 先创建会话
    create_resp = client.post("/api/sessions/", json={
        "title": "lifecycle-test",
        "mode": "localhost",
    })
    assert create_resp.status_code == 200
    session_id = create_resp.json()["id"]

    # 暂停
    pause_resp = client.post(f"/api/sessions/{session_id}/pause")
    assert pause_resp.status_code == 200
    assert pause_resp.json()["status"] == "paused"

    # 恢复
    resume_resp = client.post(f"/api/sessions/{session_id}/resume")
    assert resume_resp.status_code == 200
    assert resume_resp.json()["status"] == "running"


def test_session_lifecycle_fork(client):
    """会话生命周期 - 分叉."""
    create_resp = client.post("/api/sessions/", json={
        "title": "fork-source",
        "mode": "localhost",
    })
    assert create_resp.status_code == 200
    session_id = create_resp.json()["id"]

    fork_resp = client.post(f"/api/sessions/{session_id}/fork")
    assert fork_resp.status_code == 200
    assert "fork" in fork_resp.json()["title"]


# ---------------------------------------------------------------------------
# Devbox API
# ---------------------------------------------------------------------------

def test_devbox_status_not_found(client):
    resp = client.get("/api/devbox/nonexistent/status")
    assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Secrets API
# ---------------------------------------------------------------------------

def test_secrets_crud(client):
    # 创建
    resp = client.post("/api/secrets/", json={"name": "MY_KEY", "value": "v1"})
    assert resp.status_code == 200
    secret_id = resp.json()["id"]
    assert resp.json()["name"] == "MY_KEY"

    # 列出
    resp = client.get("/api/secrets/")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1

    # 更新
    resp = client.put(f"/api/secrets/{secret_id}", json={"value": "v2"})
    assert resp.status_code == 200

    # 删除
    resp = client.delete(f"/api/secrets/{secret_id}")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Blueprints API
# ---------------------------------------------------------------------------

def test_blueprints_list(client):
    resp = client.get("/api/blueprints/")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 3  # 默认3个模板


def test_blueprints_crud(client):
    resp = client.post("/api/blueprints/", json={
        "name": "Test BP",
        "initialize": "echo hello",
    })
    assert resp.status_code == 200
    bp_id = resp.json()["id"]

    resp = client.get(f"/api/blueprints/{bp_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Test BP"

    resp = client.get(f"/api/blueprints/{bp_id}/yaml")
    assert resp.status_code == 200
    assert "echo hello" in resp.json()["yaml"]


# ---------------------------------------------------------------------------
# Skills API
# ---------------------------------------------------------------------------

def test_skills_crud(client):
    resp = client.post("/api/skills/repo1", json={
        "name": "my-skill",
        "description": "A skill",
    })
    assert resp.status_code == 200

    resp = client.get("/api/skills/repo1")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


# ---------------------------------------------------------------------------
# API Keys API
# ---------------------------------------------------------------------------

def test_apikeys_crud(client):
    resp = client.post("/api/api-keys/", json={
        "name": "Test Bot",
        "permissions": ["read"],
    })
    assert resp.status_code == 200
    user_id = resp.json()["id"]
    assert "api_key" in resp.json()

    resp = client.get("/api/api-keys/")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1

    resp = client.delete(f"/api/api-keys/{user_id}")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Audit API
# ---------------------------------------------------------------------------

def test_audit_query(client):
    resp = client.get("/api/audit/")
    assert resp.status_code == 200

    resp = client.get("/api/audit/export")
    assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Repos API
# ---------------------------------------------------------------------------

def test_repos_crud(client):
    resp = client.post("/api/repos/", json={
        "name": "test/repo",
        "url": "https://github.com/test/repo",
        "language": "Python",
    })
    assert resp.status_code == 200
    repo_id = resp.json()["id"]

    resp = client.get("/api/repos/")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1

    resp = client.get("/api/repos/search?q=test")
    assert resp.status_code == 200

    resp = client.delete(f"/api/repos/{repo_id}")
    assert resp.status_code == 200
