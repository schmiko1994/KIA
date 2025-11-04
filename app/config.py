"""Application configuration management"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "TikTok Automation System"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./tiktok_automation.db"
    
    # Security
    secret_key: str = "change-this-secret-key-in-production"
    encryption_key: str = "change-this-encryption-key-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 1440
    
    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    cors_allow_credentials: bool = True
    
    # LLM / OpenAI
    llm_api_key: str = ""
    llm_model: str = "gpt-4-turbo-preview"
    llm_max_tokens: int = 2000
    llm_temperature: float = 0.7
    
    # ToTo Service
    toto_api_url: str = "http://localhost:7860"
    toto_api_key: str = ""
    toto_timeout: int = 300
    
    # ComfyUI Service
    comfyui_api_url: str = "http://localhost:8188"
    comfyui_timeout: int = 600
    
    # TikTok Upload
    tiktok_headless: bool = False
    tiktok_upload_timeout: int = 300
    tiktok_max_retries: int = 3
    
    # File Storage
    upload_dir: str = "./uploads"
    max_upload_size: int = 524288000  # 500MB
    allowed_video_formats: str = "mp4,mov,avi,mkv"
    
    # Logging
    log_level: str = "INFO"
    log_dir: str = "./logs"
    log_retention_days: int = 30
    
    # Workers
    enable_upload_worker: bool = True
    enable_metrics_worker: bool = True
    upload_worker_interval: int = 60
    metrics_worker_interval: int = 300
    
    # Scheduler
    scheduler_max_retries: int = 3
    scheduler_retry_delay: int = 300
    
    # Proxy
    proxy_health_check_interval: int = 600
    proxy_timeout: int = 30
    
    # Notifications
    webhook_url: str = ""
    slack_webhook_url: str = ""
    discord_webhook_url: str = ""
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    
    # Metrics
    metrics_collection_enabled: bool = True
    metrics_retention_days: int = 90
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string into list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def allowed_video_formats_list(self) -> List[str]:
        """Parse allowed video formats string into list"""
        return [fmt.strip() for fmt in self.allowed_video_formats.split(",")]


# Global settings instance
settings = Settings()
