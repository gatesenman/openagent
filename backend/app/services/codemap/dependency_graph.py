"""依赖关系图 / Dependency graph.

构建模块间的依赖关系图，检测循环依赖。
"""

from dataclasses import dataclass, field

from app.services.codemap.analyzer import ModuleInfo


@dataclass
class DependencyEdge:
    """依赖边."""
    source: str
    target: str
    import_type: str = "direct"  # direct / re-export / dynamic


class DependencyGraph:
    """模块依赖关系图.

    用于 CodeMap 的依赖可视化。
    """

    def __init__(self):
        self.nodes: list[dict] = []
        self.edges: list[DependencyEdge] = []
        self._adjacency: dict[str, list[str]] = {}

    def build(self, modules: list[ModuleInfo]) -> dict:
        """从模块列表构建依赖图."""
        module_map = {m.path: m for m in modules}
        module_names = {m.name: m.path for m in modules}

        self.nodes = []
        self.edges = []
        self._adjacency = {}

        # 创建节点
        for module in modules:
            self.nodes.append({
                "id": module.path,
                "name": module.name,
                "language": module.language,
                "size": module.size_lines,
                "complexity": module.complexity,
                "symbols": module.symbols,
            })
            self._adjacency[module.path] = []

        # 创建边
        for module in modules:
            for imp in module.imports:
                # 解析导入路径到模块路径
                target = self._resolve_import(imp, module.path, module_names, module_map)
                if target and target != module.path:
                    edge = DependencyEdge(
                        source=module.path,
                        target=target,
                    )
                    self.edges.append(edge)
                    self._adjacency.setdefault(module.path, []).append(target)

        return self.to_json()

    def find_circular(self) -> list[list[str]]:
        """检测循环依赖."""
        cycles: list[list[str]] = []
        visited: set[str] = set()
        path: list[str] = []
        in_path: set[str] = set()

        def dfs(node: str):
            if node in in_path:
                cycle_start = path.index(node)
                cycles.append(path[cycle_start:] + [node])
                return
            if node in visited:
                return

            visited.add(node)
            in_path.add(node)
            path.append(node)

            for neighbor in self._adjacency.get(node, []):
                dfs(neighbor)

            path.pop()
            in_path.remove(node)

        for node in self._adjacency:
            if node not in visited:
                dfs(node)

        return cycles

    def to_json(self) -> dict:
        """导出为前端可渲染的 JSON 格式."""
        return {
            "nodes": self.nodes,
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "type": e.import_type,
                }
                for e in self.edges
            ],
            "cycles": self.find_circular(),
            "mermaid": self.to_mermaid(),
            "dot": self.to_dot(),
            "stats": {
                "total_nodes": len(self.nodes),
                "total_edges": len(self.edges),
                "has_cycles": len(self.find_circular()) > 0,
            },
        }

    def to_mermaid(self) -> str:
        """导出为 Mermaid 图表语法（前端可直接渲染）."""
        lines = ["graph TD"]
        # 节点
        for node in self.nodes:
            safe_id = node["id"].replace("/", "_").replace(".", "_").replace("-", "_")
            label = node["name"]
            lines.append(f"    {safe_id}[{label}]")
        # 边
        for edge in self.edges:
            src = edge.source.replace("/", "_").replace(".", "_").replace("-", "_")
            tgt = edge.target.replace("/", "_").replace(".", "_").replace("-", "_")
            lines.append(f"    {src} --> {tgt}")
        return "\n".join(lines)

    def to_dot(self) -> str:
        """导出为 DOT 格式（Graphviz 可渲染）."""
        lines = ["digraph dependencies {"]
        lines.append("    rankdir=LR;")
        lines.append('    node [shape=box, style=filled, fillcolor="#e8e8e8"];')
        for node in self.nodes:
            safe_id = node["id"].replace("/", "_").replace(".", "_").replace("-", "_")
            lines.append(f'    {safe_id} [label="{node["name"]}"];')
        for edge in self.edges:
            src = edge.source.replace("/", "_").replace(".", "_").replace("-", "_")
            tgt = edge.target.replace("/", "_").replace(".", "_").replace("-", "_")
            lines.append(f"    {src} -> {tgt};")
        lines.append("}")
        return "\n".join(lines)

    def _resolve_import(
        self,
        import_path: str,
        source_path: str,
        module_names: dict[str, str],
        module_map: dict[str, ModuleInfo],
    ) -> str | None:
        """将导入路径解析为模块路径."""
        # 直接匹配模块名
        if import_path in module_names:
            return module_names[import_path]

        # 相对路径解析
        if import_path.startswith("."):
            import os
            source_dir = os.path.dirname(source_path)
            resolved = os.path.normpath(os.path.join(source_dir, import_path))
            for ext in ["", ".py", ".js", ".ts", ".tsx", ".jsx"]:
                candidate = resolved + ext
                if candidate in module_map:
                    return candidate

        # 部分匹配（模块名包含在导入路径中）
        import_parts = import_path.replace("/", ".").replace("\\", ".").split(".")
        for name, path in module_names.items():
            if name in import_parts:
                return path

        return None
