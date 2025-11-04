"""Script/Content model"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ScriptStatus(str, enum.Enum):
    """Script status enumeration"""
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    USED = "used"


class Script(Base):
    """Content script model"""
    
    __tablename__ = "scripts"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Script details
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)  # Main script content
    description = Column(Text)
    
    # Status
    status = Column(SQLEnum(ScriptStatus), default=ScriptStatus.DRAFT, nullable=False, index=True)
    
    # Trend relationship
    trend_id = Column(Integer, ForeignKey("trends.id", ondelete="SET NULL"), nullable=True, index=True)
    trend = relationship("Trend", back_populates="scripts")
    
    # Content metadata
    target_duration = Column(Integer)  # Target video duration in seconds
    hashtags = Column(JSON)  # List of hashtags
    caption = Column(Text)  # Video caption
    call_to_action = Column(String(500))
    
    # Generation metadata
    generated_by_llm = Column(String(100))  # LLM model used
    generation_prompt = Column(Text)  # Prompt used for generation
    generation_params = Column(JSON)  # Generation parameters
    
    # Quality metrics
    quality_score = Column(Integer)  # 0-100
    estimated_engagement = Column(Integer)  # Estimated engagement score
    
    # Relationships
    videos = relationship("Video", back_populates="script")
    
    # Metadata
    notes = Column(Text)
    tags = Column(String(500))  # Comma-separated tags
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    approved_at = Column(DateTime(timezone=True))
    used_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Script(id={self.id}, title='{self.title}', status='{self.status}')>"
