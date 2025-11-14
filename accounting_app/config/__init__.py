"""
Configuration Module for Bank Passbook to Accounting Converter

This module handles all configuration files including:
- Transaction categories and rules
- Account mapping for journal entries  
- Bank-specific regex patterns
- Application settings
"""

from .config_loader import config_loader
from .settings import (
    BASE_DIR, CONFIG_DIR, DATA_DIR, EXPORTS_DIR,
    APP_SETTINGS, OCR_SETTINGS, EXPORT_SETTINGS,
    get_config_path, get_export_path
)

__all__ = [
    'config_loader',
    'BASE_DIR', 'CONFIG_DIR', 'DATA_DIR', 'EXPORTS_DIR',
    'APP_SETTINGS', 'OCR_SETTINGS', 'EXPORT_SETTINGS', 
    'get_config_path', 'get_export_path'
]

# Version info
__version__ = "1.0.0"
__author__ = "Accounting Converter Team"
__description__ = "Configuration management for bank passbook processing"