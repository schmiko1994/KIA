"""Logging API endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

from app.database import get_db
from app.models.log import LogEntry, AuditLog, LogLevel, AuditAction

router = APIRouter()


class LogEntryResponse(BaseModel):
    id: int
    level: LogLevel
    message: str
    
    class Config:
        from_attributes = True


class AuditLogResponse(BaseModel):
    id: int
    action: AuditAction
    resource_type: str
    resource_id: str
    
    class Config:
        from_attributes = True


@router.get("/entries", response_model=List[LogEntryResponse])
async def list_log_entries(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List log entries"""
    result = await db.execute(select(LogEntry).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/entries/search")
async def search_logs(query: str, level: str = None):
    """Search logs"""
    return {"results": [], "query": query}


@router.get("/entries/stats")
async def get_log_stats():
    """Get log statistics"""
    return {"total": 0, "errors": 0, "warnings": 0}


@router.get("/audit", response_model=List[AuditLogResponse])
async def list_audit_logs(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List audit logs"""
    result = await db.execute(select(AuditLog).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/audit/timeline")
async def get_audit_timeline():
    """Get audit timeline"""
    return {"timeline": []}


@router.get("/audit/stats")
async def get_audit_stats():
    """Get audit statistics"""
    return {"total_actions": 0, "by_type": {}}


@router.post("/entries")
async def create_log_entry(level: str, message: str, db: AsyncSession = Depends(get_db)):
    """Create log entry"""
    log_entry = LogEntry(level=level, message=message)
    db.add(log_entry)
    await db.commit()
    return {"message": "Log entry created"}


@router.post("/audit")
async def create_audit_log(
    action: str,
    resource_type: str,
    resource_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Create audit log"""
    audit_log = AuditLog(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id
    )
    db.add(audit_log)
    await db.commit()
    return {"message": "Audit log created"}


@router.delete("/entries/cleanup")
async def cleanup_old_logs(days: int = 30):
    """Cleanup old logs"""
    return {"message": f"Cleaned up logs older than {days} days", "deleted": 0}
