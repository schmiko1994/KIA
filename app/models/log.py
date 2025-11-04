"""Log models for application and audit logging"""

from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
import enum


class LogLevel(str, enum.Enum):
    """Log level enumeration"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogEntry(Base):
    """Application log entry model"""
    
    __tablename__ = "log_entries"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Log details
    level = Column(SQLEnum(LogLevel), nullable=False, index=True)
    message = Column(Text, nullable=False)
    logger_name = Column(String(200))
    module = Column(String(200))
    function = Column(String(200))
    line_number = Column(Integer)
    
    # Context
    user_id = Column(String(100), index=True)
    session_id = Column(String(200))
    request_id = Column(String(200), index=True)
    ip_address = Column(String(50))
    
    # Additional data
    extra_data = Column(JSON)  # Additional context data
    exception_type = Column(String(200))
    exception_message = Column(Text)
    traceback = Column(Text)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<LogEntry(id={self.id}, level='{self.level}', message='{self.message[:50]}...')>"


class AuditAction(str, enum.Enum):
    """Audit action enumeration"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    UPLOAD = "upload"
    DOWNLOAD = "download"
    EXECUTE = "execute"
    APPROVE = "approve"
    REJECT = "reject"
    OTHER = "other"


class AuditLog(Base):
    """Audit log model for tracking user actions"""
    
    __tablename__ = "audit_logs"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Action details
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    resource_type = Column(String(100), nullable=False, index=True)  # account, video, schedule, etc.
    resource_id = Column(String(100), index=True)
    description = Column(Text)
    
    # User information
    user_id = Column(String(100), index=True)
    username = Column(String(200))
    ip_address = Column(String(50))
    user_agent = Column(String(500))
    
    # Request context
    request_id = Column(String(200), index=True)
    session_id = Column(String(200))
    endpoint = Column(String(500))
    method = Column(String(10))  # GET, POST, PUT, DELETE, etc.
    
    # Changes
    old_values = Column(JSON)  # Previous state
    new_values = Column(JSON)  # New state
    
    # Result
    success = Column(String(10), default="true")  # "true" or "false" as string
    error_message = Column(Text)
    
    # Additional data
    metadata = Column(JSON)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', resource='{self.resource_type}:{self.resource_id}', user='{self.username}')>"
