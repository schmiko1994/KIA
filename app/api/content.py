"""Content/Script generation API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.models.script import Script, ScriptStatus
from app.services.content_generator import content_generator

router = APIRouter()


class ScriptCreate(BaseModel):
    title: str
    content: str
    trend_id: Optional[int] = None


class ScriptGenerateRequest(BaseModel):
    prompt: str
    trend_id: Optional[int] = None
    target_duration: Optional[int] = None
    style: Optional[str] = None


class ScriptResponse(BaseModel):
    id: int
    title: str
    content: str
    status: ScriptStatus
    
    class Config:
        from_attributes = True


@router.post("/", response_model=ScriptResponse, status_code=status.HTTP_201_CREATED)
async def create_script(script_data: ScriptCreate, db: AsyncSession = Depends(get_db)):
    """Create script"""
    script = Script(**script_data.model_dump())
    db.add(script)
    await db.commit()
    await db.refresh(script)
    return script


@router.get("/", response_model=List[ScriptResponse])
async def list_scripts(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List scripts"""
    result = await db.execute(select(Script).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(script_id: int, db: AsyncSession = Depends(get_db)):
    """Get script"""
    result = await db.execute(select(Script).where(Script.id == script_id))
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    return script


@router.delete("/{script_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_script(script_id: int, db: AsyncSession = Depends(get_db)):
    """Delete script"""
    result = await db.execute(select(Script).where(Script.id == script_id))
    script = result.scalar_one_or_none()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    await db.delete(script)
    await db.commit()


@router.post("/generate")
async def generate_script(request: ScriptGenerateRequest, db: AsyncSession = Depends(get_db)):
    """Generate script using LLM"""
    try:
        result = await content_generator.generate_script(
            prompt=request.prompt,
            target_duration=request.target_duration,
            style=request.style
        )
        
        # Create script in database
        script = Script(
            title=request.prompt[:100],
            content=result.get("content", ""),
            trend_id=request.trend_id,
            generated_by_llm=result.get("model"),
            generation_prompt=request.prompt
        )
        db.add(script)
        await db.commit()
        await db.refresh(script)
        
        return {"script_id": script.id, "content": script.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/overview")
async def get_script_stats():
    """Get script statistics"""
    return {"total": 0, "draft": 0, "approved": 0, "used": 0}
