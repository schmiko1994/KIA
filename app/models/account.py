"""TikTok Account model"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class AccountStatus(str, enum.Enum):
    """Account status enumeration"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    PENDING = "pending"


class Account(Base):
    """TikTok account model"""
    
    __tablename__ = "accounts"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Account details
    username = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200))
    email = Column(String(255), unique=True, index=True)
    phone = Column(String(50))
    bio = Column(Text)
    
    # Status
    status = Column(SQLEnum(AccountStatus), default=AccountStatus.PENDING, nullable=False, index=True)
    is_verified = Column(Boolean, default=False)
    
    # Relationships
    proxy_id = Column(Integer, ForeignKey("proxies.id", ondelete="SET NULL"), nullable=True)
    proxy = relationship("Proxy", back_populates="accounts")
    
    # Credentials (one-to-one)
    credential = relationship("Credential", back_populates="account", uselist=False, cascade="all, delete-orphan")
    
    # Related entities
    videos = relationship("Video", back_populates="account", cascade="all, delete-orphan")
    schedules = relationship("Schedule", back_populates="account", cascade="all, delete-orphan")
    kpis = relationship("KPI", back_populates="account", cascade="all, delete-orphan")
    
    # Metadata
    notes = Column(Text)
    tags = Column(String(500))  # Comma-separated tags
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True))
    last_post_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Account(id={self.id}, username='{self.username}', status='{self.status}')>"
