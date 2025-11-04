"""Content generation service using LLM"""

from typing import Optional, Dict, Any, List
import openai
from app.config import settings
from app.utils.logger import app_logger


class ContentGeneratorService:
    """Service for generating content scripts using LLM"""
    
    def __init__(self):
        """Initialize content generator with OpenAI client"""
        if settings.llm_api_key:
            openai.api_key = settings.llm_api_key
        self.model = settings.llm_model
        self.max_tokens = settings.llm_max_tokens
        self.temperature = settings.llm_temperature
    
    async def generate_script(
        self,
        prompt: str,
        trend_context: Optional[str] = None,
        target_duration: Optional[int] = None,
        style: Optional[str] = None,
        additional_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a video script using LLM
        
        Args:
            prompt: Main prompt for script generation
            trend_context: Optional context about the trend
            target_duration: Target video duration in seconds
            style: Content style (e.g., "comedy", "educational", "storytelling")
            additional_params: Additional generation parameters
            
        Returns:
            Dictionary containing generated script and metadata
        """
        try:
            # Build system message
            system_message = self._build_system_message(target_duration, style)
            
            # Build user message
            user_message = self._build_user_message(prompt, trend_context)
            
            # Call OpenAI API
            app_logger.info(f"Generating script with model: {self.model}")
            
            response = await self._call_openai_api(
                system_message=system_message,
                user_message=user_message,
                additional_params=additional_params or {}
            )
            
            # Parse response
            result = self._parse_response(response)
            
            app_logger.info(f"Script generated successfully: {len(result['content'])} characters")
            
            return result
            
        except Exception as e:
            app_logger.error(f"Error generating script: {e}")
            raise
    
    def _build_system_message(self, target_duration: Optional[int], style: Optional[str]) -> str:
        """Build system message for LLM"""
        base_message = (
            "You are a professional TikTok content creator and scriptwriter. "
            "Your task is to create engaging, viral-worthy video scripts that capture attention "
            "within the first 3 seconds and maintain viewer engagement throughout."
        )
        
        if target_duration:
            base_message += f"\n\nTarget video duration: {target_duration} seconds."
        
        if style:
            base_message += f"\n\nContent style: {style}."
        
        base_message += (
            "\n\nProvide the script in a structured format with:"
            "\n1. Hook (first 3 seconds)"
            "\n2. Main content"
            "\n3. Call-to-action"
            "\n4. Suggested hashtags"
            "\n5. Caption"
        )
        
        return base_message
    
    def _build_user_message(self, prompt: str, trend_context: Optional[str]) -> str:
        """Build user message for LLM"""
        message = f"Create a TikTok video script based on the following:\n\n{prompt}"
        
        if trend_context:
            message += f"\n\nTrend context: {trend_context}"
        
        return message
    
    async def _call_openai_api(
        self,
        system_message: str,
        user_message: str,
        additional_params: Dict[str, Any]
    ) -> Any:
        """Call OpenAI API with retry logic"""
        try:
            # Use the new OpenAI client API
            client = openai.AsyncOpenAI(api_key=settings.llm_api_key)
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                **additional_params
            )
            
            return response
            
        except Exception as e:
            app_logger.error(f"OpenAI API error: {e}")
            raise
    
    def _parse_response(self, response: Any) -> Dict[str, Any]:
        """Parse OpenAI response into structured format"""
        try:
            content = response.choices[0].message.content
            
            # Extract sections (basic parsing, can be enhanced)
            result = {
                "content": content,
                "model": self.model,
                "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else 0,
                "finish_reason": response.choices[0].finish_reason
            }
            
            # Try to extract structured sections
            sections = self._extract_sections(content)
            result.update(sections)
            
            return result
            
        except Exception as e:
            app_logger.error(f"Error parsing response: {e}")
            return {
                "content": str(response),
                "model": self.model,
                "error": str(e)
            }
    
    def _extract_sections(self, content: str) -> Dict[str, Any]:
        """Extract structured sections from content"""
        sections = {}
        
        # Simple extraction logic (can be enhanced with better parsing)
        lines = content.split('\n')
        current_section = None
        section_content = []
        
        for line in lines:
            line_lower = line.lower().strip()
            
            if 'hook' in line_lower and ':' in line:
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'hook'
                section_content = [line.split(':', 1)[1].strip() if ':' in line else '']
            elif 'hashtag' in line_lower and ':' in line:
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'hashtags'
                section_content = [line.split(':', 1)[1].strip() if ':' in line else '']
            elif 'caption' in line_lower and ':' in line:
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'caption'
                section_content = [line.split(':', 1)[1].strip() if ':' in line else '']
            elif 'call' in line_lower and 'action' in line_lower:
                if current_section:
                    sections[current_section] = '\n'.join(section_content).strip()
                current_section = 'call_to_action'
                section_content = [line.split(':', 1)[1].strip() if ':' in line else '']
            elif current_section:
                section_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(section_content).strip()
        
        return sections
    
    async def generate_caption(self, script_content: str, max_length: int = 150) -> str:
        """
        Generate a caption for a video based on script content
        
        Args:
            script_content: The video script content
            max_length: Maximum caption length
            
        Returns:
            Generated caption
        """
        try:
            client = openai.AsyncOpenAI(api_key=settings.llm_api_key)
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"Create a catchy TikTok caption (max {max_length} characters) that will drive engagement."
                    },
                    {
                        "role": "user",
                        "content": f"Script: {script_content[:500]}"
                    }
                ],
                max_tokens=100,
                temperature=0.8
            )
            
            caption = response.choices[0].message.content.strip()
            return caption[:max_length]
            
        except Exception as e:
            app_logger.error(f"Error generating caption: {e}")
            return ""
    
    async def suggest_hashtags(self, script_content: str, count: int = 5) -> List[str]:
        """
        Suggest relevant hashtags for a video
        
        Args:
            script_content: The video script content
            count: Number of hashtags to suggest
            
        Returns:
            List of suggested hashtags
        """
        try:
            client = openai.AsyncOpenAI(api_key=settings.llm_api_key)
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"Suggest {count} relevant TikTok hashtags. Return only hashtags, one per line, with # prefix."
                    },
                    {
                        "role": "user",
                        "content": f"Script: {script_content[:500]}"
                    }
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            hashtags_text = response.choices[0].message.content.strip()
            hashtags = [
                tag.strip() 
                for tag in hashtags_text.split('\n') 
                if tag.strip().startswith('#')
            ]
            
            return hashtags[:count]
            
        except Exception as e:
            app_logger.error(f"Error suggesting hashtags: {e}")
            return []


# Global service instance
content_generator = ContentGeneratorService()
