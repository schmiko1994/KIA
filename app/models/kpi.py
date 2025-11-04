"""KPI (Key Performance Indicator) model"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class KPI(Base):
    """KPI and metrics model"""
    
    __tablename__ = "kpis"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Relationships
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    account = relationship("Account", back_populates="kpis")
    
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=True, index=True)
    video = relationship("Video", back_populates="kpis")
    
    # Metric type
    metric_type = Column(String(100), nullable=False, index=True)  # account_stats, video_performance, etc.
    
    # Core metrics
    followers_count = Column(Integer, default=0)
    following_count = Column(Integer, default=0)
    total_likes = Column(Integer, default=0)
    total_videos = Column(Integer, default=0)
    
    # Video-specific metrics
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    saves = Column(Integer, default=0)
    
    # Engagement metrics
    engagement_rate = Column(Float, default=0.0)  # Percentage
    watch_time_seconds = Column(Float, default=0.0)
    average_watch_percentage = Column(Float, default=0.0)
    completion_rate = Column(Float, default=0.0)
    
    # Growth metrics
    follower_growth = Column(Integer, default=0)  # Change since last measurement
    view_growth = Column(Integer, default=0)
    engagement_growth = Column(Float, default=0.0)
    
    # Audience metrics
    audience_demographics = Column(JSON)  # Age, gender, location distribution
    top_territories = Column(JSON)  # Top countries/regions
    traffic_sources = Column(JSON)  # Where views came from
    
    # Performance scores
    virality_score = Column(Float, default=0.0)  # 0-100
    quality_score = Column(Float, default=0.0)  # 0-100
    
    # Additional data
    raw_data = Column(JSON)  # Store complete raw metrics data
    
    # Collection metadata
    collected_by = Column(String(100))  # Worker or system component
    collection_method = Column(String(100))  # API, scraping, manual, etc.
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    measured_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<KPI(id={self.id}, account_id={self.account_id}, video_id={self.video_id}, type='{self.metric_type}')>"
