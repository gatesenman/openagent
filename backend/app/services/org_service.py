"""组织管理服务 / Organization Service.

Enterprise → Organization → Team 三级隔离:
- Organization: 顶层实体, 拥有成员/仓库/会话
- Team: 组织内的团队, 可限制仓库访问
- Member: 组织成员, 分角色 (admin/member/viewer)
"""

import logging
import time
import uuid
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class Member:
    """组织成员."""
    id: str = ""
    user_id: str = ""
    org_id: str = ""
    role: str = "member"  # admin / member / viewer
    email: str = ""
    display_name: str = ""
    teams: list[str] = field(default_factory=list)
    joined_at: float = 0.0
    is_active: bool = True

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.joined_at:
            self.joined_at = time.time()


@dataclass
class Team:
    """团队."""
    id: str = ""
    org_id: str = ""
    name: str = ""
    description: str = ""
    member_ids: list[str] = field(default_factory=list)
    repo_access: list[str] = field(default_factory=list)  # 允许访问的仓库ID
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class Organization:
    """组织."""
    id: str = ""
    name: str = ""
    display_name: str = ""
    plan: str = "free"  # free / pro / enterprise
    settings: dict = field(default_factory=dict)
    created_at: float = 0.0

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = time.time()


class OrgService:
    """组织管理服务."""

    def __init__(self):
        self._orgs: dict[str, Organization] = {}
        self._members: dict[str, list[Member]] = {}  # org_id → members
        self._teams: dict[str, list[Team]] = {}  # org_id → teams

    # --- Organization ---

    def create_org(self, name: str, display_name: str = "", plan: str = "free") -> Organization:
        org = Organization(name=name, display_name=display_name or name, plan=plan)
        self._orgs[org.id] = org
        self._members[org.id] = []
        self._teams[org.id] = []
        return org

    def get_org(self, org_id: str) -> Organization | None:
        return self._orgs.get(org_id)

    def list_orgs(self) -> list[dict]:
        return [
            {"id": o.id, "name": o.name, "display_name": o.display_name,
             "plan": o.plan, "member_count": len(self._members.get(o.id, []))}
            for o in self._orgs.values()
        ]

    def update_org(self, org_id: str, **kwargs) -> Organization | None:
        org = self._orgs.get(org_id)
        if not org:
            return None
        for k, v in kwargs.items():
            if hasattr(org, k) and v is not None:
                setattr(org, k, v)
        return org

    # --- Members ---

    def add_member(
        self, org_id: str, user_id: str, email: str = "",
        display_name: str = "", role: str = "member"
    ) -> Member | None:
        if org_id not in self._orgs:
            return None
        member = Member(
            user_id=user_id, org_id=org_id, role=role,
            email=email, display_name=display_name,
        )
        self._members.setdefault(org_id, []).append(member)
        return member

    def list_members(self, org_id: str) -> list[dict]:
        return [
            {"id": m.id, "user_id": m.user_id, "email": m.email,
             "display_name": m.display_name, "role": m.role,
             "teams": m.teams, "is_active": m.is_active}
            for m in self._members.get(org_id, [])
        ]

    def update_member_role(self, org_id: str, member_id: str, role: str) -> bool:
        for m in self._members.get(org_id, []):
            if m.id == member_id:
                m.role = role
                return True
        return False

    def remove_member(self, org_id: str, member_id: str) -> bool:
        members = self._members.get(org_id, [])
        for i, m in enumerate(members):
            if m.id == member_id:
                members.pop(i)
                return True
        return False

    # --- Teams ---

    def create_team(self, org_id: str, name: str, description: str = "") -> Team | None:
        if org_id not in self._orgs:
            return None
        team = Team(org_id=org_id, name=name, description=description)
        self._teams.setdefault(org_id, []).append(team)
        return team

    def list_teams(self, org_id: str) -> list[dict]:
        return [
            {"id": t.id, "name": t.name, "description": t.description,
             "member_count": len(t.member_ids)}
            for t in self._teams.get(org_id, [])
        ]

    def add_member_to_team(self, org_id: str, team_id: str, member_id: str) -> bool:
        for t in self._teams.get(org_id, []):
            if t.id == team_id:
                if member_id not in t.member_ids:
                    t.member_ids.append(member_id)
                for m in self._members.get(org_id, []):
                    if m.id == member_id and team_id not in m.teams:
                        m.teams.append(team_id)
                return True
        return False


org_service = OrgService()
