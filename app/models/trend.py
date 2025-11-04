"""Trend model"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class TrendStatus(str, enum.Enum):
    """Trend status enumeration"""
    ACTIVE = "active"
    DECLINING = "declining"
    EXPIRED = "expired"


class TrendCategory(str, enum.Enum):
    """Trend category enumeration"""
    DANCE = "dance"
    COMEDY = "comedy"
    EDUCATION = "education"
    LIFESTYLE = "lifestyle"
    FOOD = "food"
    BEAUTY = "beauty"
    FITNESS = "fitness"
    GAMING = "gaming"
    MUSIC = "music"
    PETS = "pets"
    TRAVEL = "travel"
    OTHER = "other"


class Trend(Base):
    """Trend discovery and tracking model"""
    
    __tablename__ = "trends"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Trend details
    name = Column(String(200), nullable=False, index=True)
    hashtag = Column(String(200), index=True)
    description = Column(Text)
    category = Column(SQLEnum(TrendCategory), default=TrendCategory.OTHER, nullable=False, index=True)
    
    # Status
    status = Column(SQLEnum(TrendStatus), default=TrendStatus.ACTIVE, nullable=False, index=True)
    
    # Metrics
    view_count = Column(Integer, default=0)
    video_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    virality_score = Column(Float, default=0.0)  # Custom score 0-100
    
    # Source information
    source_url = Column(String(500))
    source_platform = Column(String(50), default="tiktok")
    discovered_by = Column(String(100))  # Method or user who discovered it
    
    # Related content
    sample_video_urls = Column(JSON)  # List of sample video URLs
    related_hashtags = Column(JSON)  # List of related hashtags
    related_sounds = Column(JSON)  # List of related sounds/music
    
    # Relationships
    scripts = relationship("Script", back_populates="trend")
    
    # Metadata
    notes = Column(Text)
    tags = Column(String(500))  # Comma-separated tags
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Trend(id={self.id}, name='{self.name}', status='{self.status}', virality_score={self.virality_score})>"
