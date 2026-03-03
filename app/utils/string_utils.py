"""
String utilities.

Provides common string manipulation functions.
"""

import hashlib
import random
import string
import unicodedata
from typing import Optional


def slugify(text: str, max_length: Optional[int] = None) -> str:
    """
    Convert text to URL-friendly slug.
    
    Args:
        text: Text to slugify
        max_length: Maximum length of slug
        
    Returns:
        Slugified string
    """
    if not text:
        return ""
    
    # Normalize unicode characters
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and special characters with hyphens
    import re
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    
    # Remove leading/trailing hyphens
    text = text.strip('-')
    
    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length].rstrip('-')
    
    return text


def truncate(text: str, length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length.
    
    Args:
        text: Text to truncate
        length: Maximum length
        suffix: Suffix to append if truncated
        
    Returns:
        Truncated string
    """
    if not text or len(text) <= length:
        return text
    
    return text[:length - len(suffix)].rstrip() + suffix


def mask_email(email: str) -> str:
    """
    Mask email address for privacy.
    
    Args:
        email: Email address to mask
        
    Returns:
        Masked email (e.g., us***@example.com)
    """
    if not email or '@' not in email:
        return email
    
    local, domain = email.rsplit('@', 1)
    
    if len(local) <= 2:
        masked_local = local[0] + '*'
    else:
        masked_local = local[:2] + '*' * (len(local) - 2)
    
    # Mask domain if long
    if len(domain) > 4 and '.' in domain:
        domain_parts = domain.rsplit('.', 1)
        masked_domain = domain_parts[0][0] + '*' * (len(domain_parts[0]) - 1) + '.' + domain_parts[1]
    else:
        masked_domain = domain
    
    return f"{masked_local}@{masked_domain}"


def mask_phone(phone: str) -> str:
    """
    Mask phone number for privacy.
    
    Args:
        phone: Phone number to mask
        
    Returns:
        Masked phone (e.g., 138****1234)
    """
    if not phone:
        return phone
    
    # Remove common separators
    import re
    digits = re.sub(r'\D', '', phone)
    
    if len(digits) <= 4:
        return '*' * len(digits)
    
    # Keep first 3 and last 4 digits
    masked = digits[:3] + '*' * (len(digits) - 7) + digits[-4:]
    
    # Add back separators for display
    return masked


def generate_random_string(
    length: int = 32,
    include_digits: bool = True,
    include_uppercase: bool = True,
    include_lowercase: bool = True,
    exclude_special: bool = True,
) -> str:
    """
    Generate random string.
    
    Args:
        length: Length of random string
        include_digits: Include digits (0-9)
        include_uppercase: Include uppercase letters (A-Z)
        include_lowercase: Include lowercase letters (a-z)
        exclude_special: Exclude special characters
        
    Returns:
        Random string
    """
    chars = ""
    
    if include_digits:
        chars += string.digits
    if include_uppercase:
        chars += string.ascii_uppercase
    if include_lowercase:
        chars += string.ascii_lowercase
    
    if not exclude_special:
        chars += string.punctuation
    
    if not chars:
        chars = string.ascii_letters
    
    return ''.join(random.choice(chars) for _ in range(length))


def generate_token(length: int = 32) -> str:
    """Generate a random token (hex string)."""
    return hashlib.sha256(
        generate_random_string(length).encode()
    ).hexdigest()[:length]


def camel_to_snake(text: str) -> str:
    """
    Convert camelCase to snake_case.
    
    Args:
        text: camelCase string
        
    Returns:
        snake_case string
    """
    import re
    text = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', text).lower()


def snake_to_camel(text: str, capitalize_first: bool = False) -> str:
    """
    Convert snake_case to camelCase.
    
    Args:
        text: snake_case string
        capitalize_first: Capitalize first letter (for class names)
        
    Returns:
        camelCase string
    """
    components = text.split('_')
    
    if capitalize_first:
        return ''.join(x.title() for x in components)
    
    return components[0] + ''.join(x.title() for x in components[1:])


def clean_whitespace(text: str) -> str:
    """Clean extra whitespace from text."""
    import re
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    import re
    return re.sub(r'<[^>]+>', '', text)


def extract_numbers(text: str) -> list:
    """Extract all numbers from text."""
    import re
    return [int(x) for x in re.findall(r'\d+', text)]


def capitalize_words(text: str) -> str:
    """Capitalize first letter of each word."""
    return ' '.join(word.capitalize() for word in text.split())


def remove_special_chars(text: str, keep: str = "") -> str:
    """Remove special characters, optionally keeping some."""
    import re
    pattern = f'[^a-zA-Z0-9{re.escape(keep)}]'
    return re.sub(pattern, '', text)
