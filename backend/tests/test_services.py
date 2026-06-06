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
