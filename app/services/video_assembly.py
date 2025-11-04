"""Video assembly service"""

from typing import Optional, Dict, Any
from pathlib import Path
import ffmpeg
from app.config import settings
from app.utils.logger import app_logger


class VideoAssemblyService:
    """Service for assembling and processing videos"""
    
    def __init__(self):
        """Initialize video assembly service"""
        self.upload_dir = Path(settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def assemble_video(
        self,
        script_id: int,
        assets: Dict[str, Any],
        output_filename: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assemble a video from assets
        
        Args:
            script_id: Script ID
            assets: Dictionary of video assets (clips, images, audio, etc.)
            output_filename: Output filename
            params: Assembly parameters
            
        Returns:
            Dictionary with assembly result
        """
        try:
            app_logger.info(f"Assembling video for script {script_id}")
            
            output_path = self.upload_dir / output_filename
            
            # Basic video assembly logic
            # In production, this would integrate with ToTo/ComfyUI
            result = {
                "success": True,
                "output_path": str(output_path),
                "script_id": script_id,
                "duration": 0,
                "resolution": "1080x1920",
                "file_size": 0
            }
            
            app_logger.info(f"Video assembled successfully: {output_path}")
            
            return result
            
        except Exception as e:
            app_logger.error(f"Error assembling video: {e}")
            raise
    
    async def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """
        Get video file information
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video information
        """
        try:
            probe = ffmpeg.probe(video_path)
            video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
            audio_info = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
            
            info = {
                "duration": float(probe['format']['duration']),
                "size": int(probe['format']['size']),
                "format": probe['format']['format_name'],
                "width": int(video_info['width']),
                "height": int(video_info['height']),
                "fps": eval(video_info['r_frame_rate']),
                "codec": video_info['codec_name'],
                "has_audio": audio_info is not None
            }
            
            return info
            
        except Exception as e:
            app_logger.error(f"Error getting video info: {e}")
            raise
    
    async def create_thumbnail(
        self,
        video_path: str,
        thumbnail_path: str,
        timestamp: float = 1.0
    ) -> str:
        """
        Create thumbnail from video
        
        Args:
            video_path: Path to video file
            thumbnail_path: Output thumbnail path
            timestamp: Timestamp to capture (seconds)
            
        Returns:
            Path to created thumbnail
        """
        try:
            (
                ffmpeg
                .input(video_path, ss=timestamp)
                .filter('scale', 320, -1)
                .output(thumbnail_path, vframes=1)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            app_logger.info(f"Thumbnail created: {thumbnail_path}")
            return thumbnail_path
            
        except ffmpeg.Error as e:
            app_logger.error(f"Error creating thumbnail: {e.stderr.decode()}")
            raise
    
    async def convert_video(
        self,
        input_path: str,
        output_path: str,
        target_format: str = "mp4",
        resolution: Optional[str] = None,
        bitrate: Optional[str] = None
    ) -> str:
        """
        Convert video to different format/resolution
        
        Args:
            input_path: Input video path
            output_path: Output video path
            target_format: Target format (mp4, mov, etc.)
            resolution: Target resolution (e.g., "1080x1920")
            bitrate: Target bitrate (e.g., "2M")
            
        Returns:
            Path to converted video
        """
        try:
            stream = ffmpeg.input(input_path)
            
            # Apply filters
            if resolution:
                width, height = resolution.split('x')
                stream = stream.filter('scale', int(width), int(height))
            
            # Output options
            output_options = {}
            if bitrate:
                output_options['video_bitrate'] = bitrate
            
            (
                stream
                .output(output_path, **output_options)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            app_logger.info(f"Video converted: {output_path}")
            return output_path
            
        except ffmpeg.Error as e:
            app_logger.error(f"Error converting video: {e.stderr.decode()}")
            raise
    
    async def merge_videos(
        self,
        video_paths: list,
        output_path: str,
        transition: Optional[str] = None
    ) -> str:
        """
        Merge multiple videos into one
        
        Args:
            video_paths: List of video file paths
            output_path: Output video path
            transition: Optional transition effect
            
        Returns:
            Path to merged video
        """
        try:
            # Create concat file
            concat_file = self.upload_dir / "concat_list.txt"
            with open(concat_file, 'w') as f:
                for video_path in video_paths:
                    f.write(f"file '{video_path}'\n")
            
            (
                ffmpeg
                .input(str(concat_file), format='concat', safe=0)
                .output(output_path, c='copy')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            # Clean up concat file
            concat_file.unlink()
            
            app_logger.info(f"Videos merged: {output_path}")
            return output_path
            
        except ffmpeg.Error as e:
            app_logger.error(f"Error merging videos: {e.stderr.decode()}")
            raise
    
    async def add_audio(
        self,
        video_path: str,
        audio_path: str,
        output_path: str,
        volume: float = 1.0
    ) -> str:
        """
        Add audio track to video
        
        Args:
            video_path: Input video path
            audio_path: Audio file path
            output_path: Output video path
            volume: Audio volume (0.0 to 1.0)
            
        Returns:
            Path to video with audio
        """
        try:
            video = ffmpeg.input(video_path)
            audio = ffmpeg.input(audio_path)
            
            (
                ffmpeg
                .output(
                    video,
                    audio,
                    output_path,
                    vcodec='copy',
                    acodec='aac',
                    audio_bitrate='192k',
                    **{'filter:a': f'volume={volume}'}
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            app_logger.info(f"Audio added to video: {output_path}")
            return output_path
            
        except ffmpeg.Error as e:
            app_logger.error(f"Error adding audio: {e.stderr.decode()}")
            raise


# Global service instance
video_assembly = VideoAssemblyService()
