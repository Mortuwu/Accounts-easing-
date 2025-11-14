import re
from typing import Optional, Dict, Any

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
            },
            "pnb": {
                "keywords": ["PNB", "PUNJAB NATIONAL BANK"],
                "date_format": r"\d{2}/\d{2}/\d{4}",
                "amount_format": r"[\d,]+\.[\d]{2}"
            }
        }
    
    def detect_bank_format(self, text: str) -> str:
        """
        Detect bank format from text content
        Returns bank type or 'generic' if not detected
        """
        text_upper = text.upper()
        
        # Check for bank-specific keywords
        for bank_type, indicators in self.bank_indicators.items():
            keywords = indicators.get("keywords", [])
            for keyword in keywords:
                if keyword.upper() in text_upper:
                    return bank_type
        
        # Check date format patterns
        date_matches = self._detect_by_date_format(text)
        if date_matches:
            return date_matches
        
        # Check amount format patterns
        amount_matches = self._detect_by_amount_format(text)
        if amount_matches:
            return amount_matches
        
        return "generic"
    
    def _detect_by_date_format(self, text: str) -> Optional[str]:
        """Detect bank format based on date pattern prevalence"""
        date_patterns = {
            "sbi": r"\d{2}-\d{2}-\d{4}",  # DD-MM-YYYY
            "hdfc": r"\d{2}/\d{2}/\d{4}",  # DD/MM/YYYY
            "icici": r"\d{2}/\d{2}/\d{4}", # DD/MM/YYYY
            "axis": r"\d{2}/\d{2}/\d{4}"   # DD/MM/YYYY
        }
        
        pattern_counts = {}
        for bank_type, pattern in date_patterns.items():
            matches = re.findall(pattern, text)
            pattern_counts[bank_type] = len(matches)
        
        # Return bank with most date matches
        if pattern_counts:
            max_bank = max(pattern_counts, key=pattern_counts.get)
            if pattern_counts[max_bank] > 0:
                return max_bank
        
        return None
    
    def _detect_by_amount_format(self, text: str) -> Optional[str]:
        """Detect bank format based on amount formatting"""
        # This is a simpler approach - most Indian banks use similar amount formats
        # We can extend this for international banks if needed
        amount_pattern = r"[\d,]+\.\d{2}"
        matches = re.findall(amount_pattern, text)
        
        if len(matches) > 5:  # Reasonable number of transactions found
            # Check if amounts have comma formatting (Indian style)
            comma_formatted = any(',' in amount for amount in matches)
            if comma_formatted:
                return "generic"  # Indian bank format
        
        return None
    
    def get_bank_specific_rules(self, bank_type: str) -> Dict[str, Any]:
        """Get parsing rules for specific bank type"""
        return self.bank_indicators.get(bank_type, {})
    
    def add_custom_bank_format(self, bank_name: str, keywords: list, date_format: str, amount_format: str):
        """Add custom bank format detection"""
        self.bank_indicators[bank_name.lower()] = {
            "keywords": keywords,
            "date_format": date_format,
            "amount_format": amount_format
        }