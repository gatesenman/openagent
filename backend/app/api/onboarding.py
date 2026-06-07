"""用户引导 API / Onboarding endpoints.

交互式新手教程、示例项目、Prompt 模板库、环境预设。
"""

from typing import Optional

from fastapi import APIRouter, Query

from app.services.onboarding_service import onboarding_service

router = APIRouter()


@router.get("/steps")
async def get_onboarding_steps():
    """获取引导步骤列表."""
    return {"steps": onboarding_service.get_steps()}


@router.get("/progress/{user_id}")
async def get_user_progress(user_id: str):
    """获取用户引导进度."""
    return onboarding_service.get_user_progress(user_id)


@router.post("/progress/{user_id}/complete/{step_id}")
async def complete_step(user_id: str, step_id: str):
    """标记引导步骤完成."""
    return onboarding_service.complete_step(user_id, step_id)


@router.post("/progress/{user_id}/skip")
async def skip_onboarding(user_id: str):
    """跳过引导流程."""
    return onboarding_service.skip_onboarding(user_id)


@router.get("/samples")
async def get_sample_projects():
    """获取示例项目列表."""
    return {"projects": onboarding_service.get_sample_projects()}


@router.get("/templates")
async def get_prompt_templates(category: Optional[str] = Query(None)):
    """获取 Prompt 模板库."""
    return {"templates": onboarding_service.get_prompt_templates(category)}


@router.get("/presets")
async def get_environment_presets():
    """获取环境预设模板."""
    return {"presets": onboarding_service.get_environment_presets()}
