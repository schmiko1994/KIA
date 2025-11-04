"""ComfyUI integration service"""

from typing import Dict, Any, Optional
import httpx
from app.config import settings
from app.utils.logger import app_logger


class ComfyUIService:
    """Service for ComfyUI workflow integration"""
    
    def __init__(self):
        """Initialize ComfyUI service"""
        self.api_url = settings.comfyui_api_url
        self.timeout = settings.comfyui_timeout
    
    async def execute_workflow(
        self,
        workflow: Dict[str, Any],
        inputs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute ComfyUI workflow
        
        Args:
            workflow: Workflow definition
            inputs: Input parameters
            
        Returns:
            Execution result
        """
        try:
            app_logger.info("Executing ComfyUI workflow")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "workflow": workflow,
                    "inputs": inputs or {}
                }
                
                response = await client.post(
                    f"{self.api_url}/prompt",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                app_logger.info(f"ComfyUI workflow executed: {result.get('prompt_id')}")
                
                return result
                
        except httpx.HTTPError as e:
            app_logger.error(f"ComfyUI API error: {e}")
            raise
        except Exception as e:
            app_logger.error(f"Error executing ComfyUI workflow: {e}")
            raise
    
    async def get_workflow_status(self, prompt_id: str) -> Dict[str, Any]:
        """
        Get workflow execution status
        
        Args:
            prompt_id: Prompt/workflow ID
            
        Returns:
            Workflow status
        """
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(
                    f"{self.api_url}/history/{prompt_id}"
                )
                response.raise_for_status()
                
                return response.json()
                
        except Exception as e:
            app_logger.error(f"Error getting ComfyUI status: {e}")
            raise
    
    async def list_workflows(self) -> list:
        """
        List available workflows
        
        Returns:
            List of available workflows
        """
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(f"{self.api_url}/workflows")
                response.raise_for_status()
                
                return response.json()
                
        except Exception as e:
            app_logger.error(f"Error listing ComfyUI workflows: {e}")
            return []
    
    async def download_output(self, filename: str, output_path: str) -> str:
        """
        Download workflow output
        
        Args:
            filename: Output filename from ComfyUI
            output_path: Local output path
            
        Returns:
            Path to downloaded file
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.api_url}/view",
                    params={"filename": filename}
                )
                response.raise_for_status()
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                app_logger.info(f"ComfyUI output downloaded: {output_path}")
                return output_path
                
        except Exception as e:
            app_logger.error(f"Error downloading ComfyUI output: {e}")
            raise


# Global service instance
comfyui_service = ComfyUIService()
