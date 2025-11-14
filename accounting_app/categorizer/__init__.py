"""
Categorization Module for Bank Passbook to Accounting Converter

This module handles transaction categorization including:
- Rule-based categorization with keyword matching
- AI-powered classification using machine learning
- Category management and analytics
- Confidence scoring and validation
"""

from .rule_engine import RuleEngine
from .ai_classifier import AIClassifier
from .category_manager import CategoryManager

__all__ = [
    'RuleEngine',
    'AIClassifier', 
    'CategoryManager'
]

# Version info
__version__ = "1.0.0"
__author__ = "Accounting Converter Team"
__description__ = "Transaction categorization and classification"