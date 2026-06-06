"""CodeMap API — 代码结构可视化引擎.

接口:
  GET  /api/codemaps                状态概览
  POST /api/codemaps/analyze        分析项目结构
  POST /api/codemaps/dependencies   生成依赖关系图
  POST /api/codemaps/flow           生成代码流程图
  POST /api/codemaps/overview       模块概览
"""

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.codemap.analyzer import CodeAnalyzer
from app.services.codemap.call_graph import CallGraph
from app.services.codemap.dependency_graph import DependencyGraph
from app.services.codemap.flow_generator import FlowGenerator
from app.services.codemap.metrics import MetricsAnalyzer

router = APIRouter()


class AnalyzeRequest(BaseModel):
    repo_path: str


class FlowRequest(BaseModel):
    entry_point: str
    repo_path: str


@router.get("/")
async def codemaps_status():
    """CodeMap 状态概览."""
    return {
        "status": "ready",
        "features": [
            "module_analysis",    # 模块结构分析
            "dependency_graph",   # 依赖关系图
            "flow_generation",    # 代码流程图
            "complexity_metrics", # 复杂度度量
        ],
    }


@router.post("/analyze")
async def analyze_project(req: AnalyzeRequest):
    """分析项目模块结构."""
    analyzer = CodeAnalyzer()
    modules = analyzer.analyze_directory(req.repo_path)
    return {
        "modules": [m.to_dict() for m in modules],
        "total": len(modules),
        "summary": {
            "total_files": len(modules),
            "total_lines": sum(m.size_lines for m in modules),
            "avg_complexity": (
                round(sum(m.complexity for m in modules) / len(modules), 1)
                if modules else 0
            ),
            "languages": dict(
                sorted(
                    {
                        lang: sum(1 for m in modules if m.language == lang)
                        for lang in set(m.language for m in modules)
                    }.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            ),
        },
    }


@router.post("/dependencies")
async def dependency_graph(req: AnalyzeRequest):
    """生成依赖关系图."""
    analyzer = CodeAnalyzer()
    modules = analyzer.analyze_directory(req.repo_path)

    graph = DependencyGraph()
    result = graph.build(modules)
    return result


@router.post("/flow")
async def generate_flow(req: FlowRequest):
    """生成代码流程图（复刻 Windsurf CodeMap 格式）."""
    generator = FlowGenerator()
    steps = await generator.generate_flow(req.entry_point, req.repo_path)
    return {
        "entry_point": req.entry_point,
        "steps": [s.to_dict() for s in steps],
        "total_steps": len(steps),
    }


@router.post("/overview")
async def module_overview(req: AnalyzeRequest):
    """生成模块概览树."""
    generator = FlowGenerator()
    overview = await generator.generate_module_overview(req.repo_path)
    return overview


@router.post("/callgraph")
async def call_graph(req: AnalyzeRequest):
    """生成函数调用图."""
    cg = CallGraph()
    result = cg.build(req.repo_path)
    return result


@router.post("/metrics")
async def code_metrics(req: AnalyzeRequest):
    """代码度量指标（复杂度/行数/注释率/函数长度）."""
    analyzer = MetricsAnalyzer()
    result = analyzer.analyze(req.repo_path)
    return result
