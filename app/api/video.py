"""Video management API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from pathlib import Path

from app.database import get_db
from app.models.video import Video, VideoStatus
from app.config import settings

router = APIRouter()


class VideoCreate(BaseModel):
    title: str
    description: str
    account_id: int
    script_id: int


class VideoResponse(BaseModel):
    id: int
    title: str
    status: VideoStatus
    account_id: int
    
    class Config:
        from_attributes = True


@router.post("/", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def create_video(video_data: VideoCreate, db: AsyncSession = Depends(get_db)):
    """Create video record"""
    video = Video(**video_data.model_dump())
    db.add(video)
    await db.commit()
    await db.refresh(video)
    return video


@router.get("/", response_model=List[VideoResponse])
async def list_videos(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List videos"""
    result = await db.execute(select(Video).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(video_id: int, db: AsyncSession = Depends(get_db)):
    """Get video"""
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(video_id: int, db: AsyncSession = Depends(get_db)):
    """Delete video"""
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    await db.delete(video)
    await db.commit()


@router.post("/upload")
async def upload_video_file(file: UploadFile = File(...)):
    """Upload video file"""
    try:
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        return {"filename": file.filename, "path": str(file_path), "size": len(content)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assemble")
async def assemble_video(script_id: int):
    """Assemble video from script"""
    return {"message": "Video assembly initiated", "script_id": script_id}


@router.get("/stats/overview")
async def get_video_stats():
    """Get video statistics"""
    return {"total": 0, "pending": 0, "ready": 0, "uploaded": 0}
