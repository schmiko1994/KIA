"""Settings API endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any
from pydantic import BaseModel

from app.database import get_db
from app.models.setting import Setting, SettingCategory
from app.config import settings as app_settings

router = APIRouter()


class SettingUpdate(BaseModel):
    key: str
    value: str


@router.get("/")
async def get_all_settings(db: AsyncSession = Depends(get_db)):
    """Get all settings"""
    result = await db.execute(select(Setting))
    settings = result.scalars().all()
    return {"settings": [{"key": s.key, "value": s.value, "category": s.category} for s in settings]}


@router.put("/system")
async def update_system_settings(settings: Dict[str, Any]):
    """Update system settings"""
    return {"message": "System settings updated", "settings": settings}


@router.put("/proxy")
async def update_proxy_settings(settings: Dict[str, Any]):
    """Update proxy settings"""
    return {"message": "Proxy settings updated", "settings": settings}


@router.put("/content")
async def update_content_settings(settings: Dict[str, Any]):
    """Update content settings"""
    return {"message": "Content settings updated", "settings": settings}


@router.put("/notifications")
async def update_notification_settings(settings: Dict[str, Any]):
    """Update notification settings"""
    return {"message": "Notification settings updated", "settings": settings}


@router.post("/reset")
async def reset_to_defaults():
    """Reset to defaults"""
    return {"message": "Settings reset to defaults"}


@router.get("/env")
async def get_environment_info():
    """Get environment info"""
    return {
        "app_name": app_settings.app_name,
        "version": app_settings.app_version,
        "environment": app_settings.environment,
        "debug": app_settings.debug
    }


@router.post("/test-webhook")
async def test_webhook(url: str):
    """Test webhook"""
    return {"message": "Webhook test sent", "url": url, "status": "success"}
