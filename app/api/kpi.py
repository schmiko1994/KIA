"""KPI and metrics API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.models.kpi import KPI
from app.services.metrics_collector import metrics_collector

router = APIRouter()


class KPICreate(BaseModel):
    account_id: int
    video_id: int
    metric_type: str


class KPIResponse(BaseModel):
    id: int
    account_id: int
    metric_type: str
    views: int
    likes: int
    engagement_rate: float
    
    class Config:
        from_attributes = True


@router.post("/", response_model=KPIResponse, status_code=status.HTTP_201_CREATED)
async def create_kpi(kpi_data: KPICreate, db: AsyncSession = Depends(get_db)):
    """Create KPI record"""
    kpi = KPI(**kpi_data.model_dump())
    db.add(kpi)
    await db.commit()
    await db.refresh(kpi)
    return kpi


@router.get("/", response_model=List[KPIResponse])
async def list_kpis(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List KPIs"""
    result = await db.execute(select(KPI).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/overview")
async def get_metrics_overview():
    """Get metrics overview"""
    return {
        "total_views": 0,
        "total_likes": 0,
        "total_engagement": 0.0,
        "avg_engagement_rate": 0.0
    }


@router.get("/trends")
async def get_metric_trends():
    """Get metric trends"""
    return {"trends": []}


@router.post("/collect/{account_id}")
async def collect_account_metrics(account_id: int, db: AsyncSession = Depends(get_db)):
    """Collect account metrics"""
    try:
        metrics = await metrics_collector.collect_account_metrics(account_id)
        
        kpi = KPI(
            account_id=account_id,
            metric_type="account_stats",
            followers_count=metrics.get("followers_count", 0),
            total_likes=metrics.get("total_likes", 0)
        )
        db.add(kpi)
        await db.commit()
        
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/collect/video/{video_id}")
async def collect_video_metrics(video_id: int, db: AsyncSession = Depends(get_db)):
    """Collect video metrics"""
    try:
        metrics = await metrics_collector.collect_video_metrics(video_id, "")
        
        kpi = KPI(
            video_id=video_id,
            metric_type="video_performance",
            views=metrics.get("views", 0),
            likes=metrics.get("likes", 0)
        )
        db.add(kpi)
        await db.commit()
        
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/leaderboard")
async def get_leaderboard():
    """Get top performers"""
    return {"leaderboard": []}
