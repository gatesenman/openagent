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
