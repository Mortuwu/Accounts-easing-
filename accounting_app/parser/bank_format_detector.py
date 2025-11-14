import re
from typing import Optional

class BankFormatDetector:
    def __init__(self):
        self.bank_indicators = {
            "hdfc": {
                "keywords": ["HDFC", "HDFC BANK", "HDFC Bank"],
                "date_format": r"\d{2}/\d{2}/\d{4}",
                "amount_format": r"[\d,]+\.[\d]{2}"
            },
            "sbi": {
                "keywords": ["SBI", "STATE BANK", "State Bank of India"],
                "date_format": r"\d{2}-\d{2}-\d{4}",
                "amount_format": r"[\d,]+\.[\d]{2}"
            },
            "icici": {
                "keywords": ["ICICI", "ICICI BANK", "ICICI Bank"],
                "date_format": r"\d{2}/\d{2}/\d{4}",
                "amount_format": r"[\d,]+\.[\d]{2}"
            },
            "axis": {
                "keywords": ["AXIS", "AXIS BANK", "Axis Bank"],
                "date_format": r"\d{2}/\d{2}/\d{4}",
                "amount_format": r"[\d,]+\.[\d]{2}"
            }
        }
    
    def detect_bank_format(self, text: str) -> str:
        """Detect bank format from text content"""
        text_upper = text.upper()
        
        for bank_type, indicators in self.bank_indicators.items():
            keywords = indicators.get("keywords", [])
            for keyword in keywords:
                if keyword.upper() in text_upper:
                    return bank_type
        
        return "generic"