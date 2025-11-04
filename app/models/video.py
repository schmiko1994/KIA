"""Video model"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class VideoStatus(str, enum.Enum):
    """Video status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    UPLOADED = "uploaded"
    FAILED = "failed"
    DELETED = "deleted"


class Video(Base):
    """Video metadata model"""
    
    __tablename__ = "videos"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Video details
    title = Column(String(200), nullable=False)
    description = Column(Text)
    file_path = Column(String(500))  # Local file path
    file_size = Column(Integer)  # File size in bytes
    duration = Column(Float)  # Duration in seconds
    
    # Status
    status = Column(SQLEnum(VideoStatus), default=VideoStatus.PENDING, nullable=False, index=True)
    
    # Relationships
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=True, index=True)
    account = relationship("Account", back_populates="videos")
    
    script_id = Column(Integer, ForeignKey("scripts.id", ondelete="SET NULL"), nullable=True, index=True)
    script = relationship("Script", back_populates="videos")
    
    # Video metadata
    thumbnail_path = Column(String(500))
    resolution = Column(String(50))  # e.g., "1080x1920"
    fps = Column(Integer)  # Frames per second
    codec = Column(String(50))
    format = Column(String(50))
    
    # TikTok specific
    tiktok_video_id = Column(String(100), unique=True, index=True)
    tiktok_url = Column(String(500))
    caption = Column(Text)
    hashtags = Column(String(500))  # Comma-separated hashtags
    
    # Assembly information
    assembled_by = Column(String(100))  # ToTo, ComfyUI, manual, etc.
    assembly_workflow_id = Column(String(200))
    assembly_params = Column(Text)  # JSON string of assembly parameters
    
    # Performance metrics (updated by KPI collection)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    
    # Flags
    is_public = Column(Boolean, default=True)
    is_monetized = Column(Boolean, default=False)
    
    # Relationships
    schedules = relationship("Schedule", back_populates="video")
    kpis = relationship("KPI", back_populates="video", cascade="all, delete-orphan")
    
    # Metadata
    notes = Column(Text)
    tags = Column(String(500))  # Comma-separated tags
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    uploaded_at = Column(DateTime(timezone=True))
    published_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Video(id={self.id}, title='{self.title}', status='{self.status}')>"
