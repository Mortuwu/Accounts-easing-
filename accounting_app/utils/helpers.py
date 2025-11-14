"""
Utility functions for the Accounting Converter application
"""

import re
import uuid
from datetime import datetime
from typing import Any, Optional, Union

def validate_amount(amount: Any) -> tuple[bool, Optional[float]]:
    """
    Validate and convert amount to float
    
    Args:
        amount: Amount value to validate
        
    Returns:
        tuple: (is_valid, converted_amount)
    """
    try:
        if amount is None:
            return False, None
        
        # Handle string amounts with currency symbols and commas
        if isinstance(amount, str):
            # Remove currency symbols and commas
            clean_amount = re.sub(r'[^\d.-]', '', amount)
            if not clean_amount:
                return False, None
            amount_float = float(clean_amount)
        else:
            amount_float = float(amount)
        
        # Check if amount is positive
        if amount_float < 0:
            return False, None
            
        return True, round(amount_float, 2)
        
    except (ValueError, TypeError):
        return False, None

def validate_date(date_str: str, formats: list = None) -> tuple[bool, Optional[datetime]]:
    """
    Validate date string against multiple formats
    
    Args:
        date_str: Date string to validate
        formats: List of date formats to try
        
    Returns:
        tuple: (is_valid, datetime_object)
    """
    if formats is None:
        formats = ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d/%m/%y', '%d-%m-%y']
    
    if not date_str or not isinstance(date_str, str):
        return False, None
    
    for fmt in formats:
        try:
            date_obj = datetime.strptime(date_str.strip(), fmt)
            return True, date_obj
        except ValueError:
            continue
    
    return False, None

def format_currency(amount: float, currency_symbol: str = "₹", include_symbol: bool = True) -> str:
    """
    Format amount as currency string
    
    Args:
        amount: Amount to format
        currency_symbol: Currency symbol to use
        include_symbol: Whether to include currency symbol
        
    Returns:
        Formatted currency string
    """
    try:
        if amount is None:
            return f"{currency_symbol}0.00" if include_symbol else "0.00"
        
        amount_float = float(amount)
        formatted = f"{amount_float:,.2f}"
        
        if include_symbol:
            return f"{currency_symbol}{formatted}"
        else:
            return formatted
            
    except (ValueError, TypeError):
        return f"{currency_symbol}0.00" if include_symbol else "0.00"

def generate_unique_id(prefix: str = "") -> str:
    """
    Generate a unique identifier
    
    Args:
        prefix: Prefix for the ID
        
    Returns:
        Unique identifier string
    """
    unique_id = str(uuid.uuid4())[:8]  # First 8 characters of UUID
    if prefix:
        return f"{prefix}_{unique_id}"
    return unique_id

def clean_string(text: str, remove_extra_spaces: bool = True, 
                remove_special_chars: bool = False) -> str:
    """
    Clean and normalize string
    
    Args:
        text: Text to clean
        remove_extra_spaces: Whether to remove extra whitespace
        remove_special_chars: Whether to remove special characters
        
    Returns:
        Cleaned string
    """
    if not text:
        return ""
    
    cleaned = str(text).strip()
    
    if remove_extra_spaces:
        cleaned = re.sub(r'\s+', ' ', cleaned)
    
    if remove_special_chars:
        # Keep only alphanumeric, spaces, and basic punctuation
        cleaned = re.sub(r'[^\w\s\.\,\-\/]', '', cleaned)
    
    return cleaned

def safe_float_conversion(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float with default fallback
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Converted float value
    """
    try:
        if value is None:
            return default
        
        if isinstance(value, str):
            # Remove commas and currency symbols
            cleaned = re.sub(r'[^\d.-]', '', value)
            if not cleaned:
                return default
            return float(cleaned)
        else:
            return float(value)
            
    except (ValueError, TypeError):
        return default

def calculate_percentage(part: float, whole: float, decimal_places: int = 2) -> float:
    """
    Calculate percentage
    
    Args:
        part: Part value
        whole: Whole value
        decimal_places: Number of decimal places
        
    Returns:
        Percentage value
    """
    if whole == 0:
        return 0.0
    
    percentage = (part / whole) * 100
    return round(percentage, decimal_places)

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted file size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.2f} {size_names[i]}"

def is_valid_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        Whether email is valid
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix