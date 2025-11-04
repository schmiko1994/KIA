"""Encryption utilities for sensitive data"""

from cryptography.fernet import Fernet
from app.config import settings
import base64
import hashlib


class EncryptionService:
    """Service for encrypting and decrypting sensitive data"""
    
    def __init__(self):
        """Initialize encryption service with key from settings"""
        # Ensure the key is properly formatted for Fernet
        key = settings.encryption_key.encode()
        # Hash the key to ensure it's 32 bytes and base64 encode it
        hashed_key = hashlib.sha256(key).digest()
        self.key = base64.urlsafe_b64encode(hashed_key)
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt a string
        
        Args:
            data: Plain text string to encrypt
            
        Returns:
            Encrypted string (base64 encoded)
        """
        if not data:
            return ""
        
        encrypted_bytes = self.cipher.encrypt(data.encode())
        return encrypted_bytes.decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt a string
        
        Args:
            encrypted_data: Encrypted string (base64 encoded)
            
        Returns:
            Decrypted plain text string
        """
        if not encrypted_data:
            return ""
        
        decrypted_bytes = self.cipher.decrypt(encrypted_data.encode())
        return decrypted_bytes.decode()
    
    @staticmethod
    def generate_key() -> str:
        """
        Generate a new encryption key
        
        Returns:
            Base64 encoded encryption key
        """
        return Fernet.generate_key().decode()


# Global encryption service instance
encryption_service = EncryptionService()
