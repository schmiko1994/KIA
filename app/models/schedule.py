"""Schedule model for upload scheduling"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ScheduleStatus(str, enum.Enum):
    """Schedule status enumeration"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class ScheduleRecurrence(str, enum.Enum):
    """Schedule recurrence enumeration"""
    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Schedule(Base):
    """Upload schedule model"""
    
    __tablename__ = "schedules"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Schedule details
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Status
    status = Column(SQLEnum(ScheduleStatus), default=ScheduleStatus.PENDING, nullable=False, index=True)
    
    # Relationships
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    account = relationship("Account", back_populates="schedules")
    
    video_id = Column(Integer, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    video = relationship("Video", back_populates="schedules")
    
    # Timing
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    recurrence = Column(SQLEnum(ScheduleRecurrence), default=ScheduleRecurrence.ONCE, nullable=False)
    recurrence_end_date = Column(DateTime(timezone=True))
    
    # Execution
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    retry_delay_seconds = Column(Integer, default=300)  # 5 minutes
    
    # Priority
    priority = Column(Integer, default=5)  # 1-10, higher is more important
    
    # Relationships
    jobs = relationship("Job", back_populates="schedule", cascade="all, delete-orphan")
    
    # Metadata
    notes = Column(Text)
    tags = Column(String(500))  # Comma-separated tags
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_executed_at = Column(DateTime(timezone=True))
    next_execution_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Schedule(id={self.id}, name='{self.name}', status='{self.status}', scheduled_at='{self.scheduled_at}')>"
