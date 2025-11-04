"""Credential model for encrypted storage"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Credential(Base):
    """Encrypted credential storage model"""
    
    __tablename__ = "credentials"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Account relationship (one-to-one)
    account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    account = relationship("Account", back_populates="credential")
    
    # Encrypted credentials
    password_encrypted = Column(Text, nullable=False)  # Encrypted password
    session_token_encrypted = Column(Text)  # Encrypted session token
    cookies_encrypted = Column(Text)  # Encrypted cookies JSON
    
    # Two-factor authentication
    totp_secret_encrypted = Column(Text)  # Encrypted TOTP secret
    backup_codes_encrypted = Column(Text)  # Encrypted backup codes JSON
    
    # Additional auth data
    auth_data_encrypted = Column(Text)  # Encrypted additional auth data JSON
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_used_at = Column(DateTime(timezone=True))
    
    def __repr__(self):
        return f"<Credential(id={self.id}, account_id={self.account_id})>"
