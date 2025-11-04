"""Scheduler API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models.schedule import Schedule, ScheduleStatus
from app.models.job import Job, JobStatus

router = APIRouter()


class ScheduleCreate(BaseModel):
    name: str
    account_id: int
    video_id: int
    scheduled_at: datetime


class ScheduleResponse(BaseModel):
    id: int
    name: str
    account_id: int
    video_id: int
    status: ScheduleStatus
    scheduled_at: datetime
    
    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    id: int
    job_type: str
    status: JobStatus
    
    class Config:
        from_attributes = True


@router.post("/schedules", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(schedule_data: ScheduleCreate, db: AsyncSession = Depends(get_db)):
    """Create schedule"""
    schedule = Schedule(**schedule_data.model_dump())
    db.add(schedule)
    await db.commit()
    await db.refresh(schedule)
    return schedule


@router.get("/schedules", response_model=List[ScheduleResponse])
async def list_schedules(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List schedules"""
    result = await db.execute(select(Schedule).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/schedules/{schedule_id}", response_model=ScheduleResponse)
async def get_schedule(schedule_id: int, db: AsyncSession = Depends(get_db)):
    """Get schedule"""
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.delete("/schedules/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(schedule_id: int, db: AsyncSession = Depends(get_db)):
    """Delete schedule"""
    result = await db.execute(select(Schedule).where(Schedule.id == schedule_id))
    schedule = result.scalar_one_or_none()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    await db.delete(schedule)
    await db.commit()


@router.get("/jobs", response_model=List[JobResponse])
async def list_jobs(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List jobs"""
    result = await db.execute(select(Job).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    """Get job"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/jobs/{job_id}/retry")
async def retry_job(job_id: int, db: AsyncSession = Depends(get_db)):
    """Retry failed job"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job.status = JobStatus.QUEUED
    await db.commit()
    return {"message": "Job queued for retry", "job_id": job_id}


@router.post("/jobs/{job_id}/cancel")
async def cancel_job(job_id: int, db: AsyncSession = Depends(get_db)):
    """Cancel job"""
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job.status = JobStatus.CANCELLED
    await db.commit()
    return {"message": "Job cancelled", "job_id": job_id}


@router.get("/stats/overview")
async def get_scheduler_stats():
    """Get scheduler statistics"""
    return {"total_schedules": 0, "pending": 0, "completed": 0}


@router.post("/process-pending")
async def process_pending_jobs():
    """Process pending jobs"""
    return {"message": "Processing pending jobs", "processed": 0}
