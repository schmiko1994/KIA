"""Job model for execution tracking"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class JobStatus(str, enum.Enum):
    """Job status enumeration"""
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"


class Job(Base):
    """Job execution tracking model"""
    
    __tablename__ = "jobs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Job details
    job_type = Column(String(100), nullable=False, index=True)  # upload, metrics_collection, etc.
    description = Column(Text)
    
    # Status
    status = Column(SQLEnum(JobStatus), default=JobStatus.QUEUED, nullable=False, index=True)
    
    # Schedule relationship
    schedule_id = Column(Integer, ForeignKey("schedules.id", ondelete="CASCADE"), nullable=True, index=True)
    schedule = relationship("Schedule", back_populates="jobs")
    
    # Execution details
    attempt_number = Column(Integer, default=1)
    max_attempts = Column(Integer, default=3)
    
    # Result
    result = Column(Text)  # JSON string of result data
    error_message = Column(Text)
    error_traceback = Column(Text)
    
    # Worker information
    worker_id = Column(String(100))
    worker_hostname = Column(String(200))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    next_retry_at = Column(DateTime(timezone=True))
    
    @property
    def duration_seconds(self) -> float:
        """Calculate job duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0.0
    
    @property
    def can_retry(self) -> bool:
        """Check if job can be retried"""
        return self.attempt_number < self.max_attempts and self.status == JobStatus.FAILED
    
    def __repr__(self):
        return f"<Job(id={self.id}, type='{self.job_type}', status='{self.status}', attempt={self.attempt_number}/{self.max_attempts})>"
