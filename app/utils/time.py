"""Time utilities for ChainContext"""
import time
from datetime import datetime, timedelta
from typing import Optional


def get_current_timestamp() -> int:
    """
    Get current Unix timestamp in seconds
    
    Returns:
        Current timestamp
    """
    return int(time.time())


def format_timestamp(timestamp: int, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format Unix timestamp as a human-readable string
    
    Args:
        timestamp: Unix timestamp in seconds
        format_string: Format string for datetime.strftime
        
    Returns:
        Formatted timestamp string
    """
    return datetime.fromtimestamp(timestamp).strftime(format_string)


def get_relative_time(timestamp: int) -> str:
    """
    Get relative time from now (e.g., "2 hours ago")
    
    Args:
        timestamp: Unix timestamp in seconds
        
    Returns:
        Relative time string
    """
    now = get_current_timestamp()
    diff = now - timestamp
    
    if diff < 0:
        return "in the future"
    elif diff < 60:
        return f"{diff} seconds ago"
    elif diff < 3600:
        minutes = diff // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif diff < 86400:
        hours = diff // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif diff < 604800:
        days = diff // 86400
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif diff < 2592000:
        weeks = diff // 604800
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    elif diff < 31536000:
        months = diff // 2592000
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = diff // 31536000
        return f"{years} year{'s' if years != 1 else ''} ago"


def get_timestamp_from_relative(relative_time: str) -> Optional[int]:
    """
    Get timestamp from relative time string (e.g., "2 hours ago")
    
    Args:
        relative_time: Relative time string
        
    Returns:
        Unix timestamp in seconds, or None if parsing fails
    """
    now = get_current_timestamp()
    
    try:
        # Parse the relative time string
        if "second" in relative_time:
            seconds = int(relative_time.split()[0])
            return now - seconds
        elif "minute" in relative_time:
            minutes = int(relative_time.split()[0])
            return now - (minutes * 60)
        elif "hour" in relative_time:
            hours = int(relative_time.split()[0])
            return now - (hours * 3600)
        elif "day" in relative_time:
            days = int(relative_time.split()[0])
            return now - (days * 86400)
        elif "week" in relative_time:
            weeks = int(relative_time.split()[0])
            return now - (weeks * 604800)
        elif "month" in relative_time:
            months = int(relative_time.split()[0])
            return now - (months * 2592000)
        elif "year" in relative_time:
            years = int(relative_time.split()[0])
            return now - (years * 31536000)
        else:
            return None
    except (ValueError, IndexError):
        return None


def get_time_range(range_type: str) -> tuple:
    """
    Get start and end timestamps for a time range
    
    Args:
        range_type: Type of range (today, yesterday, this_week, this_month, this_year)
        
    Returns:
        Tuple of (start_timestamp, end_timestamp)
    """
    now = datetime.now()
    
    if range_type == "today":
        start = datetime(now.year, now.month, now.day)
        end = start + timedelta(days=1) - timedelta(seconds=1)
    elif range_type == "yesterday":
        start = datetime(now.year, now.month, now.day) - timedelta(days=1)
        end = start + timedelta(days=1) - timedelta(seconds=1)
    elif range_type == "this_week":
        start = datetime(now.year, now.month, now.day) - timedelta(days=now.weekday())
        end = start + timedelta(days=7) - timedelta(seconds=1)
    elif range_type == "this_month":
        start = datetime(now.year, now.month, 1)
        if now.month == 12:
            end = datetime(now.year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end = datetime(now.year, now.month + 1, 1) - timedelta(seconds=1)
    elif range_type == "this_year":
        start = datetime(now.year, 1, 1)
        end = datetime(now.year + 1, 1, 1) - timedelta(seconds=1)
    else:
        # Default to last 24 hours
        start = now - timedelta(days=1)
        end = now
    
    return (int(start.timestamp()), int(end.timestamp()))
