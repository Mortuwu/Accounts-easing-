import re
from typing import Union, Optional

class AmountParser:
    def __init__(self):
        self.amount_patterns = [
            r'[\d,]+\.\d{2}',      # Standard format: 1,000.00
            r'[\d,]+\.\d{1}',      # Format with one decimal: 1,000.0
            r'[\d,]+',             # Format without decimals: 1,000
            r'\d+\.\d{2}',         # Without commas: 1000.00
            r'\d+\.\d{1}',         # Without commas, one decimal: 1000.0
        ]
    
    def parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount string to float, handling various formats"""
        if not amount_str or not isinstance(amount_str, str):
            return None
        
        # Clean the amount string
        cleaned = self._clean_amount_string(amount_str)
        
        if not cleaned:
            return None
        
        try:
            # Remove commas and convert to float
            amount = float(cleaned.replace(',', ''))
            return round(amount, 2)  # Round to 2 decimal places
        except (ValueError, TypeError):
            return None
    
    def _clean_amount_string(self, amount_str: str) -> Optional[str]:
        """Clean and extract amount from string"""
        # Remove extra spaces
        amount_str = amount_str.strip()
        
        # Handle negative amounts in parentheses: (1,000.00) -> -1000.00
        if amount_str.startswith('(') and amount_str.endswith(')'):
            amount_str = '-' + amount_str[1:-1]
        
        # Try to extract amount using patterns
        for pattern in self.amount_patterns:
            match = re.search(pattern, amount_str)
            if match:
                return match.group()
        
        # If no pattern matches, try to extract digits and decimal
        digits_decimal = re.search(r'[\d,]*\.?\d+', amount_str)
        if digits_decimal:
            return digits_decimal.group()
        
        return None
    
    def validate_amount_format(self, amount_str: str) -> bool:
        """Validate if string contains a valid amount format"""
        cleaned = self._clean_amount_string(amount_str)
        if not cleaned:
            return False
        
        try:
            float(cleaned.replace(',', ''))
            return True
        except:
            return False
    
    def format_amount(self, amount: float, include_currency: bool = False) -> str:
        """Format amount as string with proper formatting"""
        try:
            # Format with commas and 2 decimal places
            formatted = "{:,.2f}".format(abs(amount))
            
            # Add negative sign if needed
            if amount < 0:
                formatted = f"({formatted})"
            
            if include_currency:
                formatted = f"₹{formatted}"
            
            return formatted
        except:
            return str(amount)