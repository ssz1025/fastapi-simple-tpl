"""
Validation utilities.

Provides common validation functions for API input validation.
"""

import re
from typing import Optional, Tuple


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"
    
    # RFC 5322 simplified email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        return False, "Invalid email format"
    
    # Length checks
    if len(email) > 254:
        return False, "Email too long"
    
    local, domain = email.rsplit('@', 1)
    if len(local) > 64:
        return False, "Email local part too long"
    
    return True, None


def validate_password_strength(
    password: str,
    min_length: int = 8,
    require_uppercase: bool = True,
    require_lowercase: bool = True,
    require_digit: bool = True,
    require_special: bool = False,
) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength.
    
    Args:
        password: Password to validate
        min_length: Minimum password length
        require_uppercase: Require uppercase letter
        require_lowercase: Require lowercase letter
        require_digit: Require digit
        require_special: Require special character
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    # Length check
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    
    if len(password) > 128:
        return False, "Password too long"
    
    # Uppercase check
    if require_uppercase and not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Lowercase check
    if require_lowercase and not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Digit check
    if require_digit and not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    # Special character check
    if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None


def validate_phone_number(
    phone: str,
    country_code: str = "CN",
) -> Tuple[bool, Optional[str]]:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
        country_code: Country code (CN, US, etc.)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return False, "Phone number is required"
    
    # Remove common separators
    phone = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Country-specific validation
    if country_code == "CN":
        # Chinese mobile: 11 digits starting with 1
        pattern = r'^1[3-9]\d{9}$'
        if not re.match(pattern, phone):
            return False, "Invalid Chinese mobile number"
    
    elif country_code == "US":
        # US phone: 10 digits
        pattern = r'^\d{10}$'
        if not re.match(pattern, phone):
            return False, "Invalid US phone number"
    
    else:
        # Generic: just digits, 7-15 characters
        pattern = r'^\d{7,15}$'
        if not re.match(pattern, phone):
            return False, "Invalid phone number format"
    
    return True, None


def validate_url(
    url: str,
    require_https: bool = False,
) -> Tuple[bool, Optional[str]]:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        require_https: Require HTTPS protocol
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL is required"
    
    # Basic URL pattern
    if require_https:
        pattern = r'^https://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    else:
        pattern = r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$'
    
    if not re.match(pattern, url):
        return False, "Invalid URL format"
    
    return True, None


def validate_username(
    username: str,
    min_length: int = 3,
    max_length: int = 30,
) -> Tuple[bool, Optional[str]]:
    """
    Validate username format.
    
    Args:
        username: Username to validate
        min_length: Minimum length
        max_length: Maximum length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"
    
    # Length check
    if len(username) < min_length:
        return False, f"Username must be at least {min_length} characters"
    
    if len(username) > max_length:
        return False, f"Username must be at most {max_length} characters"
    
    # Allowed characters: alphanumeric, underscore, hyphen
    pattern = r'^[a-zA-Z0-9_-]+$'
    if not re.match(pattern, username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"
    
    # Cannot start or end with special characters
    if username.startswith(('_', '-')) or username.endswith(('_', '-')):
        return False, "Username cannot start or end with underscore or hyphen"
    
    return True, None


def validate_json_string(json_str: str) -> Tuple[bool, Optional[str]]:
    """
    Validate JSON string format.
    
    Args:
        json_str: JSON string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    import json
    
    if not json_str:
        return False, "JSON string is required"
    
    try:
        json.loads(json_str)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"


def validate_date_range(
    start_date: str,
    end_date: str,
    format_string: str = "%Y-%m-%d",
) -> Tuple[bool, Optional[str]]:
    """
    Validate date range.
    
    Args:
        start_date: Start date string
        end_date: End date string
        format_string: Date format
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    from app.utils.datetime_utils import parse_datetime
    
    start = parse_datetime(start_date, format_string)
    end = parse_datetime(end_date, format_string)
    
    if start is None:
        return False, "Invalid start date format"
    
    if end is None:
        return False, "Invalid end date format"
    
    if start > end:
        return False, "Start date must be before end date"
    
    return True, None
