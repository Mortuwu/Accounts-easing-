"""
Utility Module for Bank Passbook to Accounting Converter

This module provides common utilities including:
- Helper functions
- Data validation
- File operations
- Common constants
"""

from .helpers import (
    validate_amount,
    validate_date,
    format_currency,
    generate_unique_id,
    clean_string,
    safe_float_conversion
)

__all__ = [
    'validate_amount',
    'validate_date', 
    'format_currency',
    'generate_unique_id',
    'clean_string',
    'safe_float_conversion'
]

# Version info
__version__ = "1.0.0"
__author__ = "Accounting Converter Team"
__description__ = "Common utility functions and helpers"