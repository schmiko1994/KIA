"""Task model for tracking operations"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
import enum


class TaskType(str, enum.Enum):
    """Task type enumeration"""
    TREND_DISCOVERY = "trend_discovery"
    SCRIPT_GENERATION = "script_generation"
    VIDEO_ASSEMBLY = "video_assembly"
    VIDEO_UPLOAD = "video_upload"
    METRICS_COLLECTION = "metrics_collection"
    PROXY_HEALTH_CHECK = "proxy_health_check"
    OTHER = "other"


class TaskStatus(str, enum.Enum):
    """Task status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(Base):
    """Task tracking model"""
    
    __tablename__ = "tasks"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Task details
    name = Column(String(200), nullable=False)
    task_type = Column(SQLEnum(TaskType), nullable=False, index=True)
    description = Column(Text)
    
    # Status
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True)
    
    # Progress
    progress = Column(Float, default=0.0)  # 0-100
    current_step = Column(String(200))
    total_steps = Column(Integer)
    
    # Result
    result = Column(Text)  # JSON string of result data
    error_message = Column(Text)
    error_traceback = Column(Text)
    
    # Execution details
    started_by = Column(String(100))  # User or system component
    worker_id = Column(String(100))  # Worker that executed the task
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    
    @property
    def duration_seconds(self) -> float:
        """Calculate task duration in seconds"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0.0
    
    def __repr__(self):
        return f"<Task(id={self.id}, name='{self.name}', type='{self.task_type}', status='{self.status}')>"
