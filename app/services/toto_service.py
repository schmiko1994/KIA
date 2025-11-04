"""ToTo integration service"""

from typing import Dict, Any, Optional
import httpx
from app.config import settings
from app.utils.logger import app_logger


class ToToService:
    """Service for ToTo video generation integration"""
    
    def __init__(self):
        """Initialize ToTo service"""
        self.api_url = settings.toto_api_url
        self.api_key = settings.toto_api_key
        self.timeout = settings.toto_timeout
    
    async def generate_video(
        self,
        prompt: str,
        duration: Optional[int] = None,
        style: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate video using ToTo
        
        Args:
            prompt: Generation prompt
            duration: Video duration
            style: Video style
            params: Additional parameters
            
        Returns:
            Generation result
        """
        try:
            app_logger.info(f"Generating video with ToTo: {prompt[:50]}...")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                payload = {
                    "prompt": prompt,
                    "duration": duration,
                    "style": style,
                    **(params or {})
                }
                
                response = await client.post(
                    f"{self.api_url}/generate",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                result = response.json()
                app_logger.info(f"ToTo generation completed: {result.get('id')}")
                
                return result
                
        except httpx.HTTPError as e:
            app_logger.error(f"ToTo API error: {e}")
            raise
        except Exception as e:
            app_logger.error(f"Error generating video with ToTo: {e}")
            raise
    
    async def get_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get ToTo job status
        
        Args:
            job_id: ToTo job ID
            
        Returns:
            Job status
        """
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                response = await client.get(
                    f"{self.api_url}/status/{job_id}",
                    headers=headers
                )
                response.raise_for_status()
                
                return response.json()
                
        except Exception as e:
            app_logger.error(f"Error getting ToTo status: {e}")
            raise
    
    async def download_result(self, job_id: str, output_path: str) -> str:
        """
        Download generated video
        
        Args:
            job_id: ToTo job ID
            output_path: Output file path
            
        Returns:
            Path to downloaded file
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                response = await client.get(
                    f"{self.api_url}/download/{job_id}",
                    headers=headers
                )
                response.raise_for_status()
                
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                app_logger.info(f"ToTo result downloaded: {output_path}")
                return output_path
                
        except Exception as e:
            app_logger.error(f"Error downloading ToTo result: {e}")
            raise


# Global service instance
toto_service = ToToService()
