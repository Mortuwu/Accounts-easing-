"""
PDF Processing Module for Bank Passbook to Accounting Converter

This module handles all PDF processing including:
- PDF type detection (digital, scanned, hybrid)
- Text extraction from digital PDFs
- OCR processing for scanned PDFs
- Text cleaning and normalization
"""

from .pdf_detector import PDFDetector
from .digital_extractor import DigitalExtractor
from .ocr_processor import OCRProcessor
from .text_cleaner import TextCleaner
from .pdf_manager import PDFManager

__all__ = [
    'PDFDetector',
    'DigitalExtractor', 
    'OCRProcessor',
    'TextCleaner',
    'PDFManager'
]

# Version info
__version__ = "1.0.0"
__author__ = "Accounting Converter Team"
__description__ = "PDF processing and text extraction utilities"