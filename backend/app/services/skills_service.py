"""Skills 管理服务 / Skills management service.

每个仓库可以有自己的 SKILL.md 文件，
定义 Agent 在该仓库中的行为模式。
"""

import logging
import time
import uuid
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Skill:
    """技能定义."""
    id: str
    repo_id: str
    name: str
    description: str = ""
    content: str = ""  # SKILL.md 内容
    path: str = ".agents/skills/SKILL.md"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "repo_id": self.repo_id,
            "name": self.name,
            "description": self.description,
            "path": self.path,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


class SkillsService:
    """Skills 管理."""

    def __init__(self):
        self._skills: dict[str, Skill] = {}

    def list_skills(self, repo_id: str) -> list[dict]:
        return [
            s.to_dict() for s in self._skills.values()
            if s.repo_id == repo_id
        ]

    def get_skill(self, skill_id: str) -> Skill | None:
        return self._skills.get(skill_id)

    def create_skill(
        self, repo_id: str, name: str, description: str = "",
        content: str = "", path: str = ".agents/skills/SKILL.md",
    ) -> Skill:
        skill = Skill(
            id=str(uuid.uuid4()),
            repo_id=repo_id,
            name=name,
            description=description,
            content=content,
            path=path,
        )
        self._skills[skill.id] = skill
        logger.info("Skill 已创建: %s (repo=%s)", name, repo_id)
        return skill

    def update_skill(self, skill_id: str, **kwargs) -> Skill | None:
        skill = self._skills.get(skill_id)
        if not skill:
            return None
        for key, value in kwargs.items():
            if hasattr(skill, key) and value is not None:
                setattr(skill, key, value)
        skill.updated_at = time.time()
        return skill

    def delete_skill(self, skill_id: str) -> bool:
        if skill_id in self._skills:
            del self._skills[skill_id]
            return True
        return False

    def parse_skill_md(self, content: str) -> dict:
        """解析 SKILL.md frontmatter."""
        result = {"name": "", "description": "", "body": content}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                import yaml
                try:
                    meta = yaml.safe_load(parts[1])
                    if isinstance(meta, dict):
                        result["name"] = meta.get("name", "")
                        result["description"] = meta.get("description", "")
                    result["body"] = parts[2].strip()
                except Exception:
                    pass
        return result


skills_service = SkillsService()
