"""知识管理器 / Knowledge manager.

管理 Agent 的知识库:
- AGENTS.md 解析 (仓库级 Agent 配置)
- 知识条目 CRUD
- 知识检索与注入
- 记忆自动发现
"""

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeEntry:
    """知识条目."""

    id: str
    name: str
    scope: str  # "system" / "user" / "repo"
    content: str
    repo_path: str = ""
    tags: list[str] = field(default_factory=list)
    pinned: bool = False
    auto_discovered: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "scope": self.scope,
            "content": self.content[:500],
            "content_length": len(self.content),
            "repo_path": self.repo_path,
            "tags": self.tags,
            "pinned": self.pinned,
            "auto_discovered": self.auto_discovered,
        }


@dataclass
class AgentsMdConfig:
    """AGENTS.md 解析结果."""

    project_name: str = ""
    description: str = ""
    tech_stack: list[str] = field(default_factory=list)
    conventions: list[str] = field(default_factory=list)
    commands: dict[str, str] = field(default_factory=dict)
    rules: list[str] = field(default_factory=list)
    raw_content: str = ""

    def to_dict(self) -> dict:
        return {
            "project_name": self.project_name,
            "description": self.description,
            "tech_stack": self.tech_stack,
            "conventions": self.conventions,
            "commands": self.commands,
            "rules": self.rules,
        }


class KnowledgeManager:
    """知识管理器.

    负责:
    1. 解析 AGENTS.md 获取仓库级知识
    2. 管理用户自定义知识条目
    3. 提供知识检索接口
    4. 自动发现和建议保存知识
    """

    def __init__(self):
        self._entries: dict[str, KnowledgeEntry] = {}
        self._agents_md_cache: dict[str, AgentsMdConfig] = {}
        self._counter = 0

        # 内置系统知识
        self._init_system_knowledge()

    def _init_system_knowledge(self) -> None:
        """初始化系统内置知识."""
        system_entries = [
            KnowledgeEntry(
                id="sys-001",
                name="代码风格",
                scope="system",
                content="遵循项目现有代码风格。优先使用项目已有的库和工具。",
                tags=["style", "convention"],
            ),
            KnowledgeEntry(
                id="sys-002",
                name="安全规范",
                scope="system",
                content="不要在代码中硬编码密钥或凭据。使用环境变量引用敏感信息。",
                tags=["security"],
            ),
            KnowledgeEntry(
                id="sys-003",
                name="测试要求",
                scope="system",
                content="新增功能需附带单元测试。修复Bug需添加回归测试。",
                tags=["testing"],
            ),
            KnowledgeEntry(
                id="sys-004",
                name="Git 规范",
                scope="system",
                content="使用语义化提交信息(feat/fix/docs/refactor)。不直接推送到main分支。",
                tags=["git"],
            ),
        ]
        for entry in system_entries:
            self._entries[entry.id] = entry

    def parse_agents_md(self, repo_path: str) -> AgentsMdConfig:
        """解析 AGENTS.md 文件.

        AGENTS.md 是仓库级的 Agent 配置文件，包含:
        - 项目描述
        - 技术栈
        - 开发规范
        - 常用命令
        - 规则约束
        """
        agents_md_path = Path(repo_path) / "AGENTS.md"
        if not agents_md_path.exists():
            return AgentsMdConfig()

        content = agents_md_path.read_text(encoding="utf-8", errors="ignore")
        config = AgentsMdConfig(raw_content=content)

        # 解析各个部分
        sections = self._split_sections(content)

        for title, body in sections.items():
            title_lower = title.lower()
            if any(kw in title_lower for kw in ["overview", "概述", "description", "简介"]):
                config.description = body.strip()
                # 提取项目名称
                first_line = body.strip().split("\n")[0]
                config.project_name = first_line.strip("# ").strip()
            elif any(kw in title_lower for kw in ["tech", "技术", "stack", "技术栈"]):
                config.tech_stack = self._extract_list(body)
            elif any(kw in title_lower for kw in ["convention", "规范", "standard", "标准"]):
                config.conventions = self._extract_list(body)
            elif any(kw in title_lower for kw in ["command", "命令", "script", "脚本"]):
                config.commands = self._extract_commands(body)
            elif any(kw in title_lower for kw in ["rule", "规则", "constraint", "约束"]):
                config.rules = self._extract_list(body)

        self._agents_md_cache[repo_path] = config
        logger.info("AGENTS.md 解析完成: %s", repo_path)
        return config

    def add_entry(
        self,
        name: str,
        content: str,
        scope: str = "user",
        repo_path: str = "",
        tags: list[str] | None = None,
        pinned: bool = False,
    ) -> KnowledgeEntry:
        """添加知识条目."""
        self._counter += 1
        entry_id = f"{scope}-{self._counter:03d}"
        entry = KnowledgeEntry(
            id=entry_id,
            name=name,
            scope=scope,
            content=content,
            repo_path=repo_path,
            tags=tags or [],
            pinned=pinned,
        )
        self._entries[entry_id] = entry
        logger.info("知识条目已添加: id=%s, name=%s", entry_id, name)
        return entry

    def get_entry(self, entry_id: str) -> KnowledgeEntry | None:
        """获取知识条目."""
        return self._entries.get(entry_id)

    def list_entries(
        self,
        scope: str | None = None,
        repo_path: str | None = None,
        tags: list[str] | None = None,
    ) -> list[KnowledgeEntry]:
        """列出知识条目."""
        entries = list(self._entries.values())

        if scope:
            entries = [e for e in entries if e.scope == scope]
        if repo_path:
            entries = [e for e in entries if e.repo_path == repo_path or e.scope == "system"]
        if tags:
            entries = [
                e for e in entries
                if any(t in e.tags for t in tags)
            ]

        return sorted(entries, key=lambda e: (not e.pinned, e.scope, e.name))

    def delete_entry(self, entry_id: str) -> bool:
        """删除知识条目."""
        if entry_id in self._entries:
            del self._entries[entry_id]
            return True
        return False

    def search(self, query: str, top_k: int = 10) -> list[KnowledgeEntry]:
        """搜索知识条目（关键词匹配）."""
        query_lower = query.lower()
        scored: list[tuple[float, KnowledgeEntry]] = []

        for entry in self._entries.values():
            score = 0.0
            if query_lower in entry.name.lower():
                score += 2.0
            if query_lower in entry.content.lower():
                score += 1.0
            for tag in entry.tags:
                if query_lower in tag.lower():
                    score += 1.5

            if score > 0:
                scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored[:top_k]]

    def get_context_for_agent(
        self, repo_path: str, task_description: str = ""
    ) -> str:
        """获取 Agent 上下文知识.

        组合系统知识 + 仓库知识 + 用户知识，注入到 Agent 的系统提示中。
        """
        context_parts: list[str] = []

        # 系统知识
        system_entries = self.list_entries(scope="system")
        if system_entries:
            context_parts.append("## 系统知识\n")
            for entry in system_entries:
                context_parts.append(f"- **{entry.name}**: {entry.content}")

        # AGENTS.md 知识
        agents_config = self._agents_md_cache.get(repo_path)
        if agents_config:
            context_parts.append("\n## 仓库配置 (AGENTS.md)\n")
            if agents_config.description:
                context_parts.append(f"项目: {agents_config.description}")
            if agents_config.conventions:
                context_parts.append("规范: " + "; ".join(agents_config.conventions))
            if agents_config.commands:
                context_parts.append("命令:")
                for cmd_name, cmd_val in agents_config.commands.items():
                    context_parts.append(f"  - {cmd_name}: `{cmd_val}`")

        # 用户知识
        user_entries = self.list_entries(scope="user", repo_path=repo_path)
        if user_entries:
            context_parts.append("\n## 用户知识\n")
            for entry in user_entries:
                context_parts.append(f"- **{entry.name}**: {entry.content}")

        return "\n".join(context_parts)

    @staticmethod
    def _split_sections(content: str) -> dict[str, str]:
        """将 Markdown 内容按标题拆分."""
        sections: dict[str, str] = {}
        current_title = "overview"
        current_body: list[str] = []

        for line in content.split("\n"):
            if line.startswith("#"):
                if current_body:
                    sections[current_title] = "\n".join(current_body)
                current_title = line.lstrip("#").strip()
                current_body = []
            else:
                current_body.append(line)

        if current_body:
            sections[current_title] = "\n".join(current_body)

        return sections

    @staticmethod
    def _extract_list(text: str) -> list[str]:
        """从 Markdown 文本中提取列表项."""
        items: list[str] = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith(("- ", "* ", "• ")):
                items.append(line[2:].strip())
            elif re.match(r"^\d+\.", line):
                items.append(re.sub(r"^\d+\.\s*", "", line).strip())
        return items

    @staticmethod
    def _extract_commands(text: str) -> dict[str, str]:
        """从文本中提取命令映射."""
        commands: dict[str, str] = {}
        for line in text.split("\n"):
            line = line.strip()
            # 匹配 `make xxx` 或 `npm xxx` 格式
            code_match = re.findall(r"`([^`]+)`", line)
            if code_match:
                for cmd in code_match:
                    name = cmd.split()[0] if " " in cmd else cmd
                    commands[name] = cmd
            # 匹配 key: value 格式
            elif ":" in line:
                parts = line.split(":", 1)
                key = parts[0].strip("- *")
                val = parts[1].strip()
                if val:
                    commands[key] = val
        return commands


# 全局实例
knowledge_manager = KnowledgeManager()
