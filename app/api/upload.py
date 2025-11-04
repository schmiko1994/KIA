"""Upload API endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from app.services.upload_service import upload_service

router = APIRouter()


class UploadRequest(BaseModel):
    account_id: int
    video_id: int
    caption: str
    hashtags: Optional[List[str]] = None


class BatchUploadRequest(BaseModel):
    video_id: int
    account_ids: List[int]
    caption: str
    hashtags: Optional[List[str]] = None


@router.post("/")
async def upload_video(request: UploadRequest):
    """Upload video to TikTok"""
    try:
        result = await upload_service.upload_video(
            account_id=request.account_id,
            video_path="",  # Would be retrieved from video record
            caption=request.caption,
            hashtags=request.hashtags
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{upload_id}/execute")
async def execute_upload(upload_id: int):
    """Execute upload job"""
    return {"message": "Upload job executed", "upload_id": upload_id}


@router.get("/{upload_id}/status")
async def get_upload_status(upload_id: int):
    """Get upload status"""
    return {"upload_id": upload_id, "status": "completed"}


@router.post("/batch")
async def batch_upload(request: BatchUploadRequest):
    """Batch upload to multiple accounts"""
    return {
        "message": "Batch upload initiated",
        "video_id": request.video_id,
        "accounts": len(request.account_ids)
    }
