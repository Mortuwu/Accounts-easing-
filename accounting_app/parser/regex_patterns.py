import re
from typing import List, Tuple, Optional
import json
from pathlib import Path

class RegexPatterns:
    def __init__(self, config_path=None):
        self.patterns = self._load_patterns(config_path)
        self.compiled_patterns = self._compile_patterns()
    
    def _load_patterns(self, config_path):
        """Load regex patterns from config or use defaults"""
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Default patterns for common bank formats
        return {
            "hdfc": [
                # DD/MM/YYYY Description Amount CR/DR Narration
                r'^(\d{1,2}/\d{1,2}/\d{2,4})\s+(.*?)\s+([\d,]+\.?\d{0,2})\s+(CR|DR)\s*(.*)$',
                # With transaction code
                r'^(\d{1,2}/\d{1,2}/\d{4})\s+([A-Z0-9/-]+)\s+(.*?)\s+([\d,]+\.?\d{0,2})\s+(CR|DR)\s*(.*)$'
            ],
            "sbi": [
                # DD-MM-YYYY Description Amount CR/DR Narration
                r'^(\d{1,2}-\d{1,2}-\d{2,4})\s+(.*?)\s+([\d,]+\.?\d{0,2})\s+(CR|DR)\s*(.*)$',
                # With cheque number
                r'^(\d{1,2}-\d{1,2}-\d{4})\s+(.*?)\s+(CHQ\s+\d+)\s+([\d,]+\.?\d{0,2})\s+(CR|DR)\s*(.*)$'
            ],
            "icici": [
                # DD/MM/YYYY Description Amount Cr/Dr Balance
                r'^(\d{1,2}/\d{1,2}/\d{4})\s+(.*?)\s+([\d,]+\.?\d{0,2})\s+(Cr|Dr)\s+([\d,]+\.?\d{0,2})$',
                # UPI transactions
                r'^(\d{1,2}/\d{1,2}/\d{4})\s+(UPI/.*?)\s+([\d,]+\.?\d{0,2})\s+(Cr|Dr)$'
            ],
            "axis": [
                # DD/MM/YYYY Description Amount CR/DR
                r'^(\d{1,2}/\d{1,2}/\d{4})\s+(.*?)\s+([\d,]+\.?\d{0,2})\s+(CR|DR)$',
                # NEFT/IMPS transactions
                r'^(\d{1,2}/\d{1,2}/\d{4})\s+(NEFT|IMPS|RTGS).*?\s+([\d,]+\.?\d{0,2})\s+(CR|DR)$'
            ],
            "generic": [
                # Generic pattern 1: Date Description Amount Type
                r'^(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(.*?)\s+([\d,]+\.?\d{0,2})\s+(CR|DR|Cr|Dr)\s*(.*)$',
                # Generic pattern 2: Date Description Type Amount
                r'^(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(.*?)\s+(CR|DR|Cr|Dr)\s+([\d,]+\.?\d{0,2})\s*(.*)$',
                # Generic pattern 3: With transaction ID
                r'^(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s+([A-Z0-9]+)\s+(.*?)\s+([\d,]+\.?\d{0,2})\s+(CR|DR)\s*(.*)$',
                # Generic pattern 4: Multi-line transactions (date on one line, details on next)
                r'^(\d{1,2}[/-]\d{1,2}[/-]\d{4})\s*$\s*^(.*?)\s+([\d,]+\.?\d{0,2})\s+(CR|DR)\s*(.*)$'
            ]
        }
    
    def _compile_patterns(self):
        """Compile all regex patterns for better performance"""
        compiled = {}
        for bank_type, patterns in self.patterns.items():
            compiled[bank_type] = [re.compile(pattern, re.IGNORECASE | re.MULTILINE) for pattern in patterns]
        return compiled
    
    def match_transaction(self, line: str, bank_type: str = "generic") -> Optional[Tuple]:
        """
        Try all patterns for a specific bank type on a line
        Returns: tuple of matched groups or None
        """
        line = line.strip()
        if not line or len(line) < 10:
            return None
        
        patterns = self.compiled_patterns.get(bank_type, []) + self.compiled_patterns.get("generic", [])
        
        for pattern in patterns:
            match = pattern.match(line)
            if match:
                return match.groups()
        
        return None
    
    def find_all_transactions(self, text: str, bank_type: str = "generic") -> List[Tuple]:
        """
        Find all transactions in text using specified bank patterns
        """
        transactions = []
        lines = text.split('\n')
        
        for line in lines:
            match = self.match_transaction(line, bank_type)
            if match:
                transactions.append(match)
        
        return transactions
    
    def get_supported_banks(self) -> List[str]:
        """Get list of supported bank formats"""
        return list(self.patterns.keys())
    
    def add_custom_pattern(self, bank_type: str, pattern: str):
        """Add custom regex pattern for a bank type"""
        if bank_type not in self.compiled_patterns:
            self.compiled_patterns[bank_type] = []
        
        compiled_pattern = re.compile(pattern, re.IGNORECASE | re.MULTILINE)
        self.compiled_patterns[bank_type].append(compiled_pattern)
        
        # Also add to patterns dict for persistence
        if bank_type not in self.patterns:
            self.patterns[bank_type] = []
        self.patterns[bank_type].append(pattern)