"""服务层测试 / Service layer tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_knowledge_manager():
    from app.services.knowledge.knowledge_manager import KnowledgeManager

    km = KnowledgeManager()

    entry = km.add_entry(
        name="test-knowledge",
        content="This is a test knowledge entry",
        scope="user",
    )
    assert entry.name == "test-knowledge"
    assert entry.scope == "user"

    found = km.get_entry(entry.id)
    assert found is not None
    assert found.content == "This is a test knowledge entry"

    results = km.search("test")
    assert len(results) > 0

    entries = km.list_entries()
    assert len(entries) > 0


def test_playbook_manager():
    from app.services.playbook.playbook_manager import PlaybookManager

    pm = PlaybookManager()

    builtins = pm.list_playbooks()
    assert len(builtins) >= 6

    names = [p.name for p in builtins]
    assert "code-review" in names or "代码审查" in names


def test_codemap_analyzer():
    import tempfile
    from pathlib import Path as P
    from app.services.codemap.analyzer import CodeAnalyzer

    with tempfile.TemporaryDirectory() as td:
        test_file = P(td) / "test.py"
        test_file.write_text(
            "import os\n\ndef hello():\n    print('hello')\n\nclass Foo:\n    pass\n",
            encoding="utf-8",
        )

        analyzer = CodeAnalyzer()
        result = analyzer.analyze_directory(td)
        assert result is not None


def test_codemap_metrics():
    import tempfile
    from pathlib import Path as P
    from app.services.codemap.metrics import MetricsAnalyzer

    with tempfile.TemporaryDirectory() as td:
        test_file = P(td) / "test.py"
        test_file.write_text(
            "def foo():\n    if True:\n        for i in range(10):\n            pass\n    return 1\n",
            encoding="utf-8",
        )

        ma = MetricsAnalyzer()
        result = ma.analyze(td)
        assert result is not None


def test_dependency_graph():
    from app.services.codemap.dependency_graph import DependencyGraph
    import tempfile
    from pathlib import Path as P

    from app.services.codemap.analyzer import CodeAnalyzer as CA2
    import tempfile as tmp2
    from pathlib import Path as P2

    with tmp2.TemporaryDirectory() as td:
        (P2(td) / "a.py").write_text("import b\n", encoding="utf-8")
        (P2(td) / "b.py").write_text("pass\n", encoding="utf-8")

        ca = CA2()
        modules = ca.analyze_directory(td)

        dg = DependencyGraph()
        dg.build(modules)

        assert len(dg.nodes) > 0

        mermaid = dg.to_mermaid()
        assert "graph TD" in mermaid


def test_deepwiki_parser():
    from app.services.deepwiki.parser import CodeParser

    parser = CodeParser()
    code = "def greet(name):\n    return f'Hello {name}'\n"
    result = parser.parse(code, "python")
    assert result is not None


def test_automation_service():
    """自动化服务测试."""
    from app.services.automation_service import automation_service

    rules = automation_service.list_rules()
    assert len(rules) >= 2

    # 创建新规则
    rule = automation_service.create_rule(
        name="test-rule",
        description="test",
        trigger_type="webhook",
    )
    assert rule.name == "test-rule"
    assert rule.id in [r.id for r in automation_service.list_rules()]

    # 删除
    assert automation_service.delete_rule(rule.id)


def test_mcp_marketplace():
    """MCP 工具市场测试."""
    from app.services.mcp_marketplace import mcp_marketplace

    servers = mcp_marketplace.list_servers()
    assert len(servers) >= 4

    # 内置筛选
    builtin = mcp_marketplace.list_servers("builtin")
    assert len(builtin) >= 3

    # 安装
    gh = mcp_marketplace.install_server("github")
    assert gh is not None
    assert gh.installed is True

    # 获取已安装工具
    tools = mcp_marketplace.get_installed_tools()
    assert len(tools) > 0


def test_task_planner():
    """任务规划器测试."""
    from app.agent.task_planner import task_planner

    plan = task_planner.decompose("实现用户登录功能")
    assert len(plan.subtasks) > 0
    assert plan.goal == "实现用户登录功能"
    assert len(plan.parallel_groups) > 0

    # 验证所有子任务都分配到了并行组中
    all_task_ids = {t.id for t in plan.subtasks}
    grouped_ids = set()
    for group in plan.parallel_groups:
        grouped_ids.update(group)
    assert all_task_ids == grouped_ids


def test_git_service_init():
    """Git 服务实例化."""
    from app.services.git_service import git_service
    assert git_service is not None


def test_rbac():
    """RBAC 权限映射测试."""
    from app.core.rbac import Permission, ROLE_PERMISSIONS
    from app.core.auth import Role

    # Admin 拥有所有权限
    assert len(ROLE_PERMISSIONS[Role.ADMIN]) == len(Permission)

    # Viewer 只有读权限
    viewer_perms = ROLE_PERMISSIONS[Role.VIEWER]
    assert Permission.SESSION_READ in viewer_perms
    assert Permission.SESSION_CREATE not in viewer_perms
    assert Permission.ADMIN_ALL not in viewer_perms


def test_secrets_service():
    from app.services.secrets_service import SecretsService

    svc = SecretsService()
    secret = svc.create_secret("TEST_KEY", "secret-value", scope="org")
    assert secret.name == "TEST_KEY"
    assert secret.scope == "org"

    # 列出时不含值
    secrets_list = svc.list_secrets()
    assert len(secrets_list) == 1
    assert "value" not in secrets_list[0]

    # 内部获取值
    val = svc.get_secret_value(secret.id)
    assert val == "secret-value"

    # 更新
    assert svc.update_secret(secret.id, "new-value")
    assert svc.get_secret_value(secret.id) == "new-value"

    # 删除
    assert svc.delete_secret(secret.id)
    assert len(svc.list_secrets()) == 0


def test_blueprint_service():
    from app.services.blueprint_service import BlueprintService

    svc = BlueprintService()
    # 默认有3个模板
    templates = svc.list_blueprints(target="template")
    assert len(templates) == 3

    # 创建新蓝图
    bp = svc.create_blueprint(
        name="Test BP",
        target="repo",
        initialize="npm install",
        maintenance="npm ci",
    )
    assert bp.name == "Test BP"
    assert "npm install" in bp.to_yaml()

    # 更新
    svc.update_blueprint(bp.id, maintenance="npm install --frozen-lockfile")
    updated = svc.get_blueprint(bp.id)
    assert updated is not None
    assert "frozen-lockfile" in updated.maintenance


def test_apikeys_service():
    from app.services.apikeys_service import APIKeysService

    svc = APIKeysService()
    user, raw_key = svc.create_service_user("CI Bot", permissions=["read", "write"])
    assert user.name == "CI Bot"
    assert raw_key.startswith("oa_")

    # 验证 key
    validated = svc.validate_api_key(raw_key)
    assert validated is not None
    assert validated.name == "CI Bot"

    # 无效 key
    assert svc.validate_api_key("invalid-key") is None

    # 禁用
    svc.toggle_service_user(user.id)
    assert svc.validate_api_key(raw_key) is None


def test_audit_service():
    from app.services.audit_service import AuditService

    svc = AuditService()
    svc.log(user_id="u1", action="session.create", resource_type="session")
    svc.log(user_id="u1", action="tool.call", resource_type="tool", severity="warning")
    svc.log(user_id="u2", action="secret.read", resource_type="secret")

    # 查询
    all_entries = svc.query()
    assert len(all_entries) == 3

    u1_entries = svc.query(user_id="u1")
    assert len(u1_entries) == 2

    warning_entries = svc.query(severity="warning")
    assert len(warning_entries) == 1


def test_repos_service():
    from app.services.repos_service import ReposService

    svc = ReposService()
    repo = svc.add_repo(
        name="test/repo",
        url="https://github.com/test/repo",
        language="Python",
    )
    assert repo.name == "test/repo"
    assert repo.deepwiki_status.value == "pending"

    # 搜索
    results = svc.search_repos("test")
    assert len(results) == 1

    # 删除
    assert svc.remove_repo(repo.id)
    assert len(svc.list_repos()) == 0


def test_skills_service():
    from app.services.skills_service import SkillsService

    svc = SkillsService()
    skill = svc.create_skill(
        repo_id="r1",
        name="test-skill",
        description="A test skill",
        content="---\nname: test\ndescription: test skill\n---\nDo things.",
    )
    assert skill.name == "test-skill"

    # 解析 frontmatter
    parsed = svc.parse_skill_md(skill.content)
    assert parsed["name"] == "test"
    assert parsed["description"] == "test skill"

    # 列出
    skills = svc.list_skills("r1")
    assert len(skills) == 1


def test_event_sourcing():
    from app.services.event_sourcing import EventStore, EventType

    store = EventStore()
    e1 = store.append("s1", EventType.AGENT_THINK, data={"thought": "planning"})
    e2 = store.append("s1", EventType.TOOL_CALL, data={"tool": "shell_exec"}, parent_event_id=e1.id)
    store.append("s1", EventType.TOOL_RESULT, data={"output": "ok"}, parent_event_id=e2.id)

    # 查询
    events = store.get_events("s1")
    assert len(events) == 3

    # 因果链
    chain = store.get_causal_chain("s1", e2.id)
    assert len(chain) == 2
    assert chain[0]["event_type"] == "agent.think"

    # 时间线
    timeline = store.get_timeline("s1")
    assert len(timeline) == 3
    assert "思考" in timeline[0]["summary"]


def test_context_manager():
    from app.agent.context_manager import ContextManager

    cm = ContextManager()
    cm.add_entry("system", "You are a helpful agent.", priority=10)
    cm.add_entry("user", "Fix the bug in main.py", priority=8)
    cm.add_entry("assistant", "I'll analyze the file.", priority=5)

    msgs = cm.get_messages()
    assert len(msgs) == 3
    assert msgs[0]["role"] == "system"

    stats = cm.get_stats()
    assert stats["entry_count"] == 3
    assert stats["total_tokens"] > 0


def test_self_healing():
    from app.agent.self_healing import SelfHealingEngine, ErrorRecord

    engine = SelfHealingEngine()

    # 记录成功
    engine.record_success()
    assert engine.get_stats()["consecutive_errors"] == 0

    # 连续3次相同错误 → 切换策略
    for i in range(3):
        result = engine.record_error(ErrorRecord(
            error_type="syntax_error",
            message="SyntaxError: unexpected token",
        ))
    assert result is not None
    assert result.value == "switch_strategy"


def test_model_router():
    from app.agent.model_router import ModelRouter, TaskComplexity

    router = ModelRouter()

    # 分类
    assert router.classify_task("rename variable x to y") == TaskComplexity.SIMPLE
    assert router.classify_task("refactor the auth module") == TaskComplexity.COMPLEX
    assert router.classify_task("fix security vulnerability") == TaskComplexity.CRITICAL

    # 选择
    fast = router.select_model(complexity=TaskComplexity.SIMPLE)
    assert fast.tier == "fast"

    strong = router.select_model(complexity=TaskComplexity.CRITICAL)
    assert strong.tier == "strong"

    # 成本预估
    estimate = router.estimate_cost("add a comment")
    assert estimate["estimated_cost"] > 0
