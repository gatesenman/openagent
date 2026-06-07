"""SSO/SAML/OIDC API."""

from fastapi import APIRouter

from app.services.sso_service import sso_service

router = APIRouter()


@router.post("/configs")
async def create_config(data: dict):
    cfg = sso_service.create_config(
        org_id=data.get("org_id", ""),
        provider=data.get("provider", "saml"),
        name=data.get("name", ""),
        entity_id=data.get("entity_id", ""),
        sso_url=data.get("sso_url", ""),
        certificate=data.get("certificate", ""),
        client_id=data.get("client_id", ""),
        issuer_url=data.get("issuer_url", ""),
        domain_whitelist=data.get("domain_whitelist", []),
    )
    return {"id": cfg.id, "provider": cfg.provider.value}


@router.get("/configs")
async def list_configs(org_id: str = ""):
    return {"configs": sso_service.list_configs(org_id)}


@router.get("/configs/{config_id}")
async def get_config(config_id: str):
    return sso_service.get_config(config_id) or {"error": "not found"}


@router.post("/configs/{config_id}/activate")
async def activate(config_id: str):
    return {"ok": sso_service.activate(config_id)}


@router.post("/configs/{config_id}/deactivate")
async def deactivate(config_id: str):
    return {"ok": sso_service.deactivate(config_id)}


@router.post("/configs/{config_id}/test")
async def test_connection(config_id: str):
    return sso_service.test_connection(config_id)


@router.post("/configs/{config_id}/login")
async def initiate_login(config_id: str):
    result = sso_service.initiate_login(config_id)
    return result or {"error": "SSO not active"}


@router.post("/callback/{config_id}")
async def handle_callback(config_id: str, data: dict):
    session = sso_service.handle_callback(
        config_id,
        code=data.get("code", ""),
        saml_response=data.get("saml_response", ""),
    )
    if not session:
        return {"error": "callback failed"}
    return {
        "token": session.token,
        "email": session.user_email,
        "name": session.user_name,
        "groups": session.groups,
    }


@router.delete("/configs/{config_id}")
async def delete_config(config_id: str):
    return {"ok": sso_service.delete_config(config_id)}
