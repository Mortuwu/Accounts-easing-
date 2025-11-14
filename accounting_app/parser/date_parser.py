import re
from datetime import datetime
from typing import Optional, Union
import dateutil.parser

class DateParser:
    def __init__(self):
        self.date_patterns = [
            (r'\d{1,2}/\d{1,2}/\d{4}', '%d/%m/%Y'),    # DD/MM/YYYY
            (r'\d{1,2}-\d{1,2}-\d{4}', '%d-%m-%Y'),    # DD-MM-YYYY
            (r'\d{1,2}\.\d{1,2}\.\d{4}', '%d.%m.%Y'),  # DD.MM.YYYY
            (r'\d{4}/\d{1,2}/\d{1,2}', '%Y/%m/%d'),    # YYYY/MM/DD
            (r'\d{4}-\d{1,2}-\d{1,2}', '%Y-%m-%d'),    # YYYY-MM-DD
            (r'\d{1,2}/\d{1,2}/\d{2}', '%d/%m/%y'),    # DD/MM/YY
            (r'\d{1,2}-\d{1,2}-\d{2}', '%d-%m-%y'),    # DD-MM-YY
        ]
    
    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string to datetime object using multiple methods"""
        if not date_str or not isinstance(date_str, str):
            return None
        
        date_str = date_str.strip()
        
        # Method 1: Try specific patterns first
        for pattern, format_str in self.date_patterns:
            if re.match(pattern, date_str):
                try:
                    return datetime.strptime(date_str, format_str)
                except ValueError:
                    continue
        
        # Method 2: Try dateutil parser (more flexible)
        try:
            return dateutil.parser.parse(date_str, dayfirst=True)
        except:
            pass
        
        # Method 3: Manual parsing for common variations
        manual_parsed = self._manual_date_parse(date_str)
        if manual_parsed:
            return manual_parsed
        
        return None
    
    def _manual_date_parse(self, date_str: str) -> Optional[datetime]:
        """Manual date parsing for tricky formats"""
        # Remove any non-date characters
        clean_date = re.sub(r'[^\d/\-\.]', '', date_str)
        
        # Try common separators
        for sep in ['/', '-', '.']:
            parts = clean_date.split(sep)
            if len(parts) == 3:
                try:
                    day, month, year = map(int, parts)
                    
                    # Handle 2-digit years
                    if year < 100:
                        year += 2000 if year < 50 else 1900
                    
                    # Validate date components
                    if 1 <= day <= 31 and 1 <= month <= 12:
                        return datetime(year, month, day)
                except:
                    continue
        
        return None
    
    def format_date(self, date_obj: datetime, format_str: str = '%d/%m/%Y') -> str:
        """Format datetime object to string"""
        try:
            return date_obj.strftime(format_str)
        except:
            return str(date_obj)
    
    def validate_date_format(self, date_str: str) -> bool:
        """Validate if string contains a valid date format"""
        return self.parse_date(date_str) is not None
    
    def detect_date_format(self, date_str: str) -> Optional[str]:
        """Detect the format of a date string"""
        for pattern, format_str in self.date_patterns:
            if re.match(pattern, date_str):
                try:
                    datetime.strptime(date_str, format_str)
                    return format_str
                except ValueError:
                    continue
        return None
    
    def get_all_date_formats(self) -> list:
        """Get all supported date formats"""
        return [format_str for _, format_str in self.date_patterns]