"""计费 API."""

from fastapi import APIRouter

from app.services.billing_service import billing_service

router = APIRouter()


@router.get("/usage/{org_id}")
async def get_usage(org_id: str):
    return billing_service.get_usage_summary(org_id)


@router.get("/quota/{org_id}")
async def check_quota(org_id: str):
    return billing_service.check_quota(org_id)


@router.post("/record")
async def record_usage(data: dict):
    record = billing_service.record_usage(
        org_id=data.get("org_id", ""),
        session_id=data.get("session_id", ""),
        duration_minutes=data.get("duration_minutes", 0),
        token_input=data.get("token_input", 0),
        token_output=data.get("token_output", 0),
    )
    return {"id": record.id, "acu_consumed": record.acu_consumed}


@router.get("/prices")
async def get_prices():
    return {"plans": billing_service.get_price_table()}
