"""
Journal Generation Module for Bank Passbook to Accounting Converter

This module handles accounting journal generation including:
- Double-entry accounting journal entries
- Accounting rules and standards compliance
- Ledger management and trial balance
- Financial reporting
"""

from .entry_generator import JournalEntryGenerator
from .accounting_rules import AccountingRules
from .ledger_manager import LedgerManager

__all__ = [
    'JournalEntryGenerator',
    'AccountingRules',
    'LedgerManager'
]

# Version info
__version__ = "1.0.0"
__author__ = "Accounting Converter Team"
__description__ = "Accounting journal generation and ledger management"