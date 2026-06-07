"""Playbook 管理器 / Playbook manager.

管理可复用的 Agent 任务模板:
- 系统内置 Playbook (代码审查/Bug修复/特性开发/测试/文档等)
- 用户自定义 Playbook
- Playbook 执行（注入系统提示 + 步骤引导）
"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PlaybookStep:
    """Playbook 步骤."""

    order: int
    instruction: str
    tool_hint: str = ""  # 建议使用的工具
    validation: str = ""  # 验证条件

    def to_dict(self) -> dict:
        result: dict = {
            "order": self.order,
            "instruction": self.instruction,
        }
        if self.tool_hint:
            result["tool_hint"] = self.tool_hint
        if self.validation:
            result["validation"] = self.validation
        return result


@dataclass
class Playbook:
    """Playbook — 可复用的 Agent 任务模板."""

    id: str
    name: str
    description: str
    scope: str = "system"  # "system" / "organization" / "user"
    category: str = "general"
    system_prompt: str = ""
    steps: list[PlaybookStep] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    variables: list[str] = field(default_factory=list)
    enabled: bool = True

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "scope": self.scope,
            "category": self.category,
            "system_prompt": self.system_prompt[:200] + "..." if len(self.system_prompt) > 200 else self.system_prompt,
            "steps": [s.to_dict() for s in self.steps],
            "tags": self.tags,
            "variables": self.variables,
            "enabled": self.enabled,
        }

    def to_full_prompt(self, variables: dict[str, str] | None = None) -> str:
        """生成完整的系统提示词."""
        prompt = self.system_prompt
        if variables:
            for key, value in variables.items():
                prompt = prompt.replace(f"{{{{{key}}}}}", value)

        if self.steps:
            prompt += "\n\n## 执行步骤\n"
            for step in self.steps:
                prompt += f"\n{step.order}. {step.instruction}"
                if step.tool_hint:
                    prompt += f"\n   工具: {step.tool_hint}"
                if step.validation:
                    prompt += f"\n   验证: {step.validation}"

        return prompt


class PlaybookManager:
    """Playbook 管理器."""

    def __init__(self):
        self._playbooks: dict[str, Playbook] = {}
        self._init_system_playbooks()

    def _init_system_playbooks(self) -> None:
        """初始化系统内置 Playbook."""
        system_playbooks = [
            Playbook(
                id="sys-code-review",
                name="代码审查",
                description="对提交的代码变更进行全面审查",
                category="review",
                system_prompt=(
                    "你是一位资深代码审查员。请仔细审查代码变更，关注：\n"
                    "1. 代码正确性和逻辑错误\n"
                    "2. 安全漏洞（SQL注入/XSS/敏感信息泄露）\n"
                    "3. 性能问题\n"
                    "4. 代码风格和可维护性\n"
                    "5. 测试覆盖率"
                ),
                steps=[
                    PlaybookStep(1, "读取 PR 描述和变更文件列表", "file_read"),
                    PlaybookStep(2, "逐文件审查代码变更", "search_code"),
                    PlaybookStep(3, "检查是否有测试覆盖", "shell_exec"),
                    PlaybookStep(4, "运行 lint 检查", "shell_exec", "lint 通过"),
                    PlaybookStep(5, "生成审查报告", "", "报告包含问题/建议/总结"),
                ],
                tags=["review", "quality"],
            ),
            Playbook(
                id="sys-bug-fix",
                name="Bug 修复",
                description="分析、定位并修复 Bug",
                category="development",
                system_prompt=(
                    "你是一位经验丰富的调试专家。请按以下流程修复 Bug：\n"
                    "1. 理解 Bug 描述和复现步骤\n"
                    "2. 定位根因（使用搜索和代码分析工具）\n"
                    "3. 实现最小修复\n"
                    "4. 添加回归测试\n"
                    "5. 验证修复不引入新问题"
                ),
                steps=[
                    PlaybookStep(1, "分析 Bug 描述，确认复现条件"),
                    PlaybookStep(2, "搜索相关代码定位问题", "search_code"),
                    PlaybookStep(3, "实现修复", "file_write"),
                    PlaybookStep(4, "添加回归测试", "file_write"),
                    PlaybookStep(5, "运行测试验证", "shell_exec", "所有测试通过"),
                    PlaybookStep(6, "提交修复", "git_ops"),
                ],
                tags=["bug", "fix", "debug"],
            ),
            Playbook(
                id="sys-feature-dev",
                name="特性开发",
                description="从需求到实现的完整特性开发流程",
                category="development",
                system_prompt=(
                    "你是一位全栈开发工程师。请按以下流程开发新特性：\n"
                    "1. 分析需求并制定实现计划\n"
                    "2. 设计方案（数据模型/API/UI）\n"
                    "3. 实现代码\n"
                    "4. 编写测试\n"
                    "5. 运行完整测试套件\n"
                    "6. 提交 PR"
                ),
                steps=[
                    PlaybookStep(1, "分析需求，制定任务计划"),
                    PlaybookStep(2, "阅读现有代码理解架构", "search_code"),
                    PlaybookStep(3, "实现核心功能", "file_write"),
                    PlaybookStep(4, "编写单元测试", "file_write"),
                    PlaybookStep(5, "运行测试", "shell_exec", "测试通过"),
                    PlaybookStep(6, "运行 lint", "shell_exec", "lint 通过"),
                    PlaybookStep(7, "创建 PR", "git_ops"),
                ],
                tags=["feature", "development"],
            ),
            Playbook(
                id="sys-test-suite",
                name="测试套件编写",
                description="为现有代码编写全面的测试套件",
                category="testing",
                system_prompt=(
                    "你是一位测试工程师。请为指定代码编写全面的测试：\n"
                    "1. 分析代码结构和功能\n"
                    "2. 设计测试用例（正常/边界/异常）\n"
                    "3. 实现单元测试\n"
                    "4. 确保测试覆盖率达标"
                ),
                steps=[
                    PlaybookStep(1, "分析目标代码的功能和接口", "file_read"),
                    PlaybookStep(2, "查看现有测试了解测试风格", "search_code"),
                    PlaybookStep(3, "编写单元测试", "file_write"),
                    PlaybookStep(4, "运行测试确认通过", "shell_exec", "所有测试通过"),
                    PlaybookStep(5, "检查覆盖率", "shell_exec"),
                ],
                tags=["test", "quality"],
            ),
            Playbook(
                id="sys-doc-gen",
                name="文档生成",
                description="为项目生成或更新文档",
                category="documentation",
                system_prompt=(
                    "你是一位技术文档工程师。请为项目生成高质量文档：\n"
                    "1. 分析项目结构和代码\n"
                    "2. 生成 API 文档\n"
                    "3. 更新 README\n"
                    "4. 添加使用示例"
                ),
                steps=[
                    PlaybookStep(1, "分析项目结构", "file_read"),
                    PlaybookStep(2, "提取 API 接口信息", "search_code"),
                    PlaybookStep(3, "生成文档", "file_write"),
                    PlaybookStep(4, "验证文档格式", "shell_exec"),
                ],
                tags=["docs", "documentation"],
            ),
            Playbook(
                id="sys-refactor",
                name="代码重构",
                description="安全地重构代码以提高质量",
                category="development",
                system_prompt=(
                    "你是一位重构专家。请安全地重构代码：\n"
                    "1. 确保有足够的测试覆盖\n"
                    "2. 小步重构，每步验证\n"
                    "3. 保持外部行为不变\n"
                    "4. 提高代码可读性和可维护性"
                ),
                steps=[
                    PlaybookStep(1, "运行现有测试确认基线", "shell_exec", "测试通过"),
                    PlaybookStep(2, "分析需要重构的代码", "file_read"),
                    PlaybookStep(3, "执行重构", "file_write"),
                    PlaybookStep(4, "运行测试验证", "shell_exec", "测试通过"),
                    PlaybookStep(5, "运行 lint", "shell_exec", "lint 通过"),
                ],
                tags=["refactor", "quality"],
            ),
        ]

        for playbook in system_playbooks:
            self._playbooks[playbook.id] = playbook

    def list_playbooks(
        self, scope: str | None = None, category: str | None = None
    ) -> list[Playbook]:
        """列出 Playbook."""
        playbooks = list(self._playbooks.values())
        if scope:
            playbooks = [p for p in playbooks if p.scope == scope]
        if category:
            playbooks = [p for p in playbooks if p.category == category]
        return sorted(playbooks, key=lambda p: p.name)

    def get_playbook(self, playbook_id: str) -> Playbook | None:
        """获取 Playbook."""
        return self._playbooks.get(playbook_id)

    def create_playbook(self, data: dict) -> Playbook:
        """创建自定义 Playbook."""
        playbook_id = f"user-{len(self._playbooks) + 1:03d}"
        steps = [
            PlaybookStep(
                order=i + 1,
                instruction=s.get("instruction", ""),
                tool_hint=s.get("tool_hint", ""),
                validation=s.get("validation", ""),
            )
            for i, s in enumerate(data.get("steps", []))
        ]
        playbook = Playbook(
            id=playbook_id,
            name=data.get("name", "自定义 Playbook"),
            description=data.get("description", ""),
            scope="user",
            category=data.get("category", "general"),
            system_prompt=data.get("system_prompt", ""),
            steps=steps,
            tags=data.get("tags", []),
            variables=data.get("variables", []),
        )
        self._playbooks[playbook_id] = playbook
        logger.info("Playbook 已创建: id=%s, name=%s", playbook_id, playbook.name)
        return playbook

    def delete_playbook(self, playbook_id: str) -> bool:
        """删除 Playbook（仅限用户自定义）."""
        playbook = self._playbooks.get(playbook_id)
        if not playbook:
            return False
        if playbook.scope == "system":
            raise ValueError("不能删除系统 Playbook")
        del self._playbooks[playbook_id]
        return True


# 全局实例
playbook_manager = PlaybookManager()
