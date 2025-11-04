"""ToTo/ComfyUI integration API endpoints"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.services.toto_service import toto_service
from app.services.comfyui_service import comfyui_service

router = APIRouter()


class ToToGenerateRequest(BaseModel):
    prompt: str
    duration: Optional[int] = None
    style: Optional[str] = None


class ComfyUIWorkflowRequest(BaseModel):
    workflow: Dict[str, Any]
    inputs: Optional[Dict[str, Any]] = None


@router.get("/status")
async def get_worker_status():
    """Get worker status"""
    return {"toto": "available", "comfyui": "available"}


@router.post("/toto/generate")
async def generate_with_toto(request: ToToGenerateRequest):
    """Generate video with ToTo"""
    try:
        result = await toto_service.generate_video(
            prompt=request.prompt,
            duration=request.duration,
            style=request.style
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/comfyui/workflow")
async def execute_comfyui_workflow(request: ComfyUIWorkflowRequest):
    """Execute ComfyUI workflow"""
    try:
        result = await comfyui_service.execute_workflow(
            workflow=request.workflow,
            inputs=request.inputs
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comfyui/workflow/{workflow_id}/status")
async def get_workflow_status(workflow_id: str):
    """Get workflow status"""
    try:
        status = await comfyui_service.get_workflow_status(workflow_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/comfyui/workflows")
async def list_workflows():
    """List available workflows"""
    try:
        workflows = await comfyui_service.list_workflows()
        return {"workflows": workflows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/render")
async def render_video(script_id: int, worker: str = "toto"):
    """Render video with worker"""
    return {"message": f"Rendering with {worker}", "script_id": script_id}
