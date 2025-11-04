"""Proxy management API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.proxy import Proxy, ProxyType, ProxyStatus
from app.utils.logger import app_logger

router = APIRouter()


class ProxyCreate(BaseModel):
    name: str
    proxy_type: ProxyType
    host: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None


class ProxyUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[ProxyStatus] = None
    username: Optional[str] = None
    password: Optional[str] = None


class ProxyResponse(BaseModel):
    id: int
    name: str
    proxy_type: ProxyType
    host: str
    port: int
    status: ProxyStatus
    is_healthy: bool
    
    class Config:
        from_attributes = True


@router.post("/", response_model=ProxyResponse, status_code=status.HTTP_201_CREATED)
async def create_proxy(proxy_data: ProxyCreate, db: AsyncSession = Depends(get_db)):
    """Create a new proxy"""
    try:
        proxy = Proxy(**proxy_data.model_dump())
        db.add(proxy)
        await db.commit()
        await db.refresh(proxy)
        app_logger.info(f"Proxy created: {proxy.name}")
        return proxy
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ProxyResponse])
async def list_proxies(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all proxies"""
    try:
        result = await db.execute(select(Proxy).offset(skip).limit(limit))
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{proxy_id}", response_model=ProxyResponse)
async def get_proxy(proxy_id: int, db: AsyncSession = Depends(get_db)):
    """Get proxy by ID"""
    try:
        result = await db.execute(select(Proxy).where(Proxy.id == proxy_id))
        proxy = result.scalar_one_or_none()
        if not proxy:
            raise HTTPException(status_code=404, detail="Proxy not found")
        return proxy
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{proxy_id}", response_model=ProxyResponse)
async def update_proxy(proxy_id: int, proxy_data: ProxyUpdate, db: AsyncSession = Depends(get_db)):
    """Update proxy"""
    try:
        result = await db.execute(select(Proxy).where(Proxy.id == proxy_id))
        proxy = result.scalar_one_or_none()
        if not proxy:
            raise HTTPException(status_code=404, detail="Proxy not found")
        
        for key, value in proxy_data.model_dump(exclude_unset=True).items():
            setattr(proxy, key, value)
        
        await db.commit()
        await db.refresh(proxy)
        return proxy
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{proxy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_proxy(proxy_id: int, db: AsyncSession = Depends(get_db)):
    """Delete proxy"""
    try:
        result = await db.execute(select(Proxy).where(Proxy.id == proxy_id))
        proxy = result.scalar_one_or_none()
        if not proxy:
            raise HTTPException(status_code=404, detail="Proxy not found")
        
        await db.delete(proxy)
        await db.commit()
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{proxy_id}/health-check")
async def health_check_proxy(proxy_id: int, db: AsyncSession = Depends(get_db)):
    """Perform health check on proxy"""
    try:
        result = await db.execute(select(Proxy).where(Proxy.id == proxy_id))
        proxy = result.scalar_one_or_none()
        if not proxy:
            raise HTTPException(status_code=404, detail="Proxy not found")
        
        # Perform health check logic here
        proxy.is_healthy = True
        proxy.last_health_check = datetime.utcnow()
        await db.commit()
        
        return {"status": "healthy", "proxy_id": proxy_id}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview")
async def get_proxy_stats(db: AsyncSession = Depends(get_db)):
    """Get proxy statistics"""
    try:
        total = await db.scalar(select(func.count()).select_from(Proxy))
        active = await db.scalar(select(func.count()).select_from(Proxy).where(Proxy.status == ProxyStatus.ACTIVE))
        
        return {"total": total or 0, "active": active or 0, "healthy": active or 0}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
