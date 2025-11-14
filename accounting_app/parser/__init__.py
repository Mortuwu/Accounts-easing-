"""
Parsing Module for Bank Passbook to Accounting Converter

This module handles all transaction parsing including:
- Regex pattern matching for different bank formats
- Transaction data extraction and validation
- Bank format detection
- Amount and date parsing
"""

from .regex_patterns import RegexPatterns
from .transaction_parser import TransactionParser
from .bank_format_detector import BankFormatDetector
from .amount_parser import AmountParser
from .date_parser import DateParser

__all__ = [
    'RegexPatterns',
    'TransactionParser',
    'BankFormatDetector',
    'AmountParser',
    'DateParser'
]

# Version info
__version__ = "1.0.0"
__author__ = "Accounting Converter Team"
__description__ = "Transaction parsing and bank format detection"