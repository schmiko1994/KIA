"""Proxy model"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ProxyType(str, enum.Enum):
    """Proxy type enumeration"""
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


class ProxyStatus(str, enum.Enum):
    """Proxy status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"


class Proxy(Base):
    """Proxy configuration model"""
    
    __tablename__ = "proxies"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Proxy details
    name = Column(String(200), nullable=False)
    proxy_type = Column(SQLEnum(ProxyType), default=ProxyType.HTTP, nullable=False)
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String(255))
    password = Column(String(255))  # Should be encrypted
    
    # Status and health
    status = Column(SQLEnum(ProxyStatus), default=ProxyStatus.ACTIVE, nullable=False, index=True)
    is_healthy = Column(Boolean, default=True)
    last_health_check = Column(DateTime(timezone=True))
    health_check_failures = Column(Integer, default=0)
    
    # Performance metrics
    response_time_ms = Column(Float)  # Average response time
    success_rate = Column(Float)  # Success rate percentage
    total_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    
    # Location
    country = Column(String(100))
    city = Column(String(100))
    
    # Relationships
    accounts = relationship("Account", back_populates="proxy")
    
    # Metadata
    notes = Column(Text)
    tags = Column(String(500))  # Comma-separated tags
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    @property
    def proxy_url(self) -> str:
        """Generate proxy URL string"""
        if self.username and self.password:
            return f"{self.proxy_type.value}://{self.username}:{self.password}@{self.host}:{self.port}"
        return f"{self.proxy_type.value}://{self.host}:{self.port}"
    
    def __repr__(self):
        return f"<Proxy(id={self.id}, name='{self.name}', host='{self.host}:{self.port}', status='{self.status}')>"
