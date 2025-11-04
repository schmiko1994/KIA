"""Trend discovery API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.models.trend import Trend, TrendStatus, TrendCategory

router = APIRouter()


class TrendCreate(BaseModel):
    name: str
    hashtag: str
    description: str
    category: TrendCategory


class TrendResponse(BaseModel):
    id: int
    name: str
    hashtag: str
    category: TrendCategory
    status: TrendStatus
    virality_score: float
    
    class Config:
        from_attributes = True


@router.post("/", response_model=TrendResponse, status_code=status.HTTP_201_CREATED)
async def create_trend(trend_data: TrendCreate, db: AsyncSession = Depends(get_db)):
    """Create trend"""
    trend = Trend(**trend_data.model_dump())
    db.add(trend)
    await db.commit()
    await db.refresh(trend)
    return trend


@router.get("/", response_model=List[TrendResponse])
async def list_trends(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List trends"""
    result = await db.execute(select(Trend).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{trend_id}", response_model=TrendResponse)
async def get_trend(trend_id: int, db: AsyncSession = Depends(get_db)):
    """Get trend"""
    result = await db.execute(select(Trend).where(Trend.id == trend_id))
    trend = result.scalar_one_or_none()
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    return trend


@router.delete("/{trend_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trend(trend_id: int, db: AsyncSession = Depends(get_db)):
    """Delete trend"""
    result = await db.execute(select(Trend).where(Trend.id == trend_id))
    trend = result.scalar_one_or_none()
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    await db.delete(trend)
    await db.commit()


@router.post("/discover")
async def discover_trends():
    """Discover new trends"""
    return {"message": "Trend discovery initiated", "trends_found": 0}


@router.get("/stats/overview")
async def get_trend_stats():
    """Get trend statistics"""
    return {"total": 0, "active": 0, "declining": 0}
