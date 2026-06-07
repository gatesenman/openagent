"""组织管理 API."""

from fastapi import APIRouter

from app.services.org_service import org_service

router = APIRouter()


@router.get("/")
async def list_orgs():
    return {"orgs": org_service.list_orgs()}


@router.post("/")
async def create_org(data: dict):
    org = org_service.create_org(
        name=data.get("name", ""),
        display_name=data.get("display_name", ""),
        plan=data.get("plan", "free"),
    )
    return {"id": org.id, "name": org.name}


@router.get("/{org_id}")
async def get_org(org_id: str):
    org = org_service.get_org(org_id)
    if not org:
        return {"error": "not found"}
    return {"id": org.id, "name": org.name, "display_name": org.display_name, "plan": org.plan}


@router.put("/{org_id}")
async def update_org(org_id: str, data: dict):
    org = org_service.update_org(org_id, **data)
    return {"ok": org is not None}


# --- Members ---

@router.get("/{org_id}/members")
async def list_members(org_id: str):
    return {"members": org_service.list_members(org_id)}


@router.post("/{org_id}/members")
async def add_member(org_id: str, data: dict):
    member = org_service.add_member(
        org_id, data.get("user_id", ""),
        email=data.get("email", ""),
        display_name=data.get("display_name", ""),
        role=data.get("role", "member"),
    )
    if not member:
        return {"error": "org not found"}
    return {"id": member.id}


@router.delete("/{org_id}/members/{member_id}")
async def remove_member(org_id: str, member_id: str):
    return {"ok": org_service.remove_member(org_id, member_id)}


@router.put("/{org_id}/members/{member_id}/role")
async def update_role(org_id: str, member_id: str, data: dict):
    return {"ok": org_service.update_member_role(org_id, member_id, data.get("role", "member"))}


# --- Teams ---

@router.get("/{org_id}/teams")
async def list_teams(org_id: str):
    return {"teams": org_service.list_teams(org_id)}


@router.post("/{org_id}/teams")
async def create_team(org_id: str, data: dict):
    team = org_service.create_team(org_id, data.get("name", ""), data.get("description", ""))
    if not team:
        return {"error": "org not found"}
    return {"id": team.id}


@router.post("/{org_id}/teams/{team_id}/members")
async def add_team_member(org_id: str, team_id: str, data: dict):
    return {"ok": org_service.add_member_to_team(org_id, team_id, data.get("member_id", ""))}
