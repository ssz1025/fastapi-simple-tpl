"""
Datetime utilities.

Provides common datetime operations for API responses and database queries.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple


def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def utc_now_timestamp() -> float:
    """Get current UTC timestamp."""
    return utc_now().timestamp()


def format_datetime(
    dt: datetime,
    format_string: str = "%Y-%m-%d %H:%M:%S",
    include_timezone: bool = False,
) -> str:
    """
    Format datetime to string.
    
    Args:
        dt: Datetime object
        format_string: Format string (default: ISO format)
        include_timezone: Whether to include timezone info
        
    Returns:
        Formatted datetime string
    """
    if dt is None:
        return ""
    
    # Ensure timezone awareness
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    result = dt.strftime(format_string)
    
    if include_timezone:
        result += f" {dt.strftime('%Z')}"
    
    return result


def parse_datetime(
    date_string: str,
    format_string: Optional[str] = None,
) -> Optional[datetime]:
    """
    Parse datetime from string.
    
    Args:
        date_string: Date string to parse
        format_string: Optional format string
        
    Returns:
        Datetime object or None if parsing fails
    """
    if not date_string:
        return None
    
    # Try ISO format first
    if format_string is None:
        try:
            # Try parsing ISO format
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt
        except ValueError:
            pass
        
        # Try common formats
        common_formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y",
            "%m/%d/%Y %H:%M:%S",
            "%m/%d/%Y",
        ]
        
        for fmt in common_formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        
        return None
    
    try:
        return datetime.strptime(date_string, format_string)
    except ValueError:
        return None


def get_date_range(
    days: int = 7,
    end_date: Optional[datetime] = None,
) -> Tuple[datetime, datetime]:
    """
    Get date range from end_date going back N days.
    
    Args:
        days: Number of days to go back
        end_date: End date (default: now)
        
    Returns:
        Tuple of (start_date, end_date)
    """
    if end_date is None:
        end_date = utc_now()
    
    start_date = end_date - timedelta(days=days)
    
    return start_date, end_date


def is_expired(
    expiry_time: datetime,
    current_time: Optional[datetime] = None,
) -> bool:
    """
    Check if a datetime has expired.
    
    Args:
        expiry_time: The expiry datetime
        current_time: Current time (default: now)
        
    Returns:
        True if expired, False otherwise
    """
    if current_time is None:
        current_time = utc_now()
    
    # Ensure both are timezone-aware
    if expiry_time.tzinfo is None:
        expiry_time = expiry_time.replace(tzinfo=timezone.utc)
    if current_time.tzinfo is None:
        current_time = current_time.replace(tzinfo=timezone.utc)
    
    return expiry_time < current_time


def add_time(
    dt: datetime,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0,
) -> datetime:
    """
    Add time to datetime.
    
    Args:
        dt: Base datetime
        days: Days to add
        hours: Hours to add
        minutes: Minutes to add
        seconds: Seconds to add
        
    Returns:
        New datetime
    """
    return dt + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)


def time_ago(dt: datetime) -> str:
    """
    Get human-readable time ago string.
    
    Args:
        dt: Datetime to compare
        
    Returns:
        String like "5 minutes ago"
    """
    now = utc_now()
    
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    diff = now - dt
    seconds = int(diff.total_seconds())
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif seconds < 604800:
        days = seconds // 86400
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif seconds < 2592000:
        weeks = seconds // 604800
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif seconds < 31536000:
        months = seconds // 2592000
        return f"{months} month{'s' if months > 1 else ''} ago"
    else:
        years = seconds // 31536000
        return f"{years} year{'s' if years > 1 else ''} ago"


def to_unix_timestamp(dt: datetime) -> int:
    """Convert datetime to Unix timestamp."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def from_unix_timestamp(timestamp: int) -> datetime:
    """Convert Unix timestamp to datetime."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
