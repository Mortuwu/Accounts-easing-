import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"

# Create directories if they don't exist
for directory in [DATA_DIR, EXPORTS_DIR]:
    directory.mkdir(exist_ok=True)

# Application settings
APP_SETTINGS = {
    "app_name": "Bank Passbook to Accounting Converter",
    "version": "1.0.0",
    "default_currency": "₹",
    "date_format": "%d/%m/%Y",
    "max_file_size_mb": 50,
    "supported_banks": ["HDFC", "SBI", "ICICI", "Axis", "PNB", "BOB", "Canara", "Standard"]
}

# OCR Settings
OCR_SETTINGS = {
    "dpi": 300,
    "preprocess": True,
    "language": "eng",
    "timeout": 60
}

# Export Settings
EXPORT_SETTINGS = {
    "excel": {
        "default_sheets": ["Transactions", "Journal Entries", "Summary"],
        "auto_format": True
    },
    "pdf": {
        "page_size": "A4",
        "font_size": 10,
        "include_summary": True
    }
}

def get_config_path(filename):
    """Get absolute path for config files"""
    return CONFIG_DIR / filename

def get_export_path(filename):
    """Get absolute path for export files"""
    return EXPORTS_DIR / filename