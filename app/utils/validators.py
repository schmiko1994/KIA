"""Input validation utilities"""

import re
from typing import Optional
from email_validator import validate_email, EmailNotValidError
import phonenumbers


def validate_email_address(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def validate_phone_number(phone: str, region: Optional[str] = None) -> bool:
    """
    Validate phone number format
    
    Args:
        phone: Phone number to validate
        region: Optional region code (e.g., 'US', 'GB')
        
    Returns:
        True if valid, False otherwise
    """
    try:
        parsed = phonenumbers.parse(phone, region)
        return phonenumbers.is_valid_number(parsed)
    except phonenumbers.NumberParseException:
        return False


def validate_url(url: str) -> bool:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def validate_proxy_format(proxy: str) -> bool:
    """
    Validate proxy string format (protocol://host:port or protocol://user:pass@host:port)
    
    Args:
        proxy: Proxy string to validate
        
    Returns:
        True if valid, False otherwise
    """
    proxy_pattern = re.compile(
        r'^(http|https|socks4|socks5)://'
        r'(?:([^:]+):([^@]+)@)?'  # optional user:pass
        r'([^:]+)'  # host
        r':(\d+)$'  # port
    )
    return proxy_pattern.match(proxy) is not None


def validate_tiktok_username(username: str) -> bool:
    """
    Validate TikTok username format
    
    Args:
        username: TikTok username to validate
        
    Returns:
        True if valid, False otherwise
    """
    # TikTok usernames: 2-24 characters, alphanumeric, underscores, dots
    username_pattern = re.compile(r'^[a-zA-Z0-9_.]{2,24}$')
    return username_pattern.match(username) is not None


def validate_hashtag(hashtag: str) -> bool:
    """
    Validate hashtag format
    
    Args:
        hashtag: Hashtag to validate (with or without #)
        
    Returns:
        True if valid, False otherwise
    """
    # Remove leading # if present
    tag = hashtag.lstrip('#')
    # Hashtags: alphanumeric and underscores, no spaces
    hashtag_pattern = re.compile(r'^[a-zA-Z0-9_]+$')
    return len(tag) > 0 and hashtag_pattern.match(tag) is not None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing/replacing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        sanitized = name[:255-len(ext)-1] + '.' + ext if ext else name[:255]
    return sanitized


def validate_video_duration(duration_seconds: int, min_duration: int = 3, max_duration: int = 600) -> bool:
    """
    Validate video duration is within acceptable range
    
    Args:
        duration_seconds: Video duration in seconds
        min_duration: Minimum allowed duration (default 3s)
        max_duration: Maximum allowed duration (default 600s/10min)
        
    Returns:
        True if valid, False otherwise
    """
    return min_duration <= duration_seconds <= max_duration
