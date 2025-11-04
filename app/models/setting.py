"""Setting model for system configuration"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from app.database import Base
import enum


class SettingCategory(str, enum.Enum):
    """Setting category enumeration"""
    SYSTEM = "system"
    PROXY = "proxy"
    CONTENT = "content"
    UPLOAD = "upload"
    NOTIFICATIONS = "notifications"
    SECURITY = "security"
    OTHER = "other"


class SettingType(str, enum.Enum):
    """Setting value type enumeration"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    JSON = "json"


class Setting(Base):
    """System settings model"""
    
    __tablename__ = "settings"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Setting identification
    key = Column(String(200), unique=True, nullable=False, index=True)
    category = Column(SQLEnum(SettingCategory), default=SettingCategory.SYSTEM, nullable=False, index=True)
    
    # Value
    value = Column(Text, nullable=False)
    value_type = Column(SQLEnum(SettingType), default=SettingType.STRING, nullable=False)
    default_value = Column(Text)
    
    # Metadata
    name = Column(String(200), nullable=False)
    description = Column(Text)
    is_sensitive = Column(String(10), default="false")  # "true" or "false" as string
    is_editable = Column(String(10), default="true")  # "true" or "false" as string
    
    # Validation
    validation_regex = Column(String(500))
    allowed_values = Column(Text)  # Comma-separated list of allowed values
    min_value = Column(Float)
    max_value = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Setting(id={self.id}, key='{self.key}', category='{self.category}')>"
