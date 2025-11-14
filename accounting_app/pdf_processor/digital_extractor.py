import pdfplumber
import fitz  # PyMuPDF
import pandas as pd
from typing import List, Dict, Any, Optional

class DigitalExtractor:
    def __init__(self):
        self.extraction_methods = ['pdfplumber', 'pymupdf']
    
    def extract_text(self, pdf_path: str, method: str = 'auto') -> str:
        """
        Extract text from digital PDF using multiple methods with fallback
        Returns the best extracted text
        """
        try:
            if method == 'auto':
                # Try multiple methods and return the best result
                results = []
                
                # Try pdfplumber first (usually best for digital PDFs)
                text_plumber = self._extract_with_pdfplumber(pdf_path)
                results.append(('pdfplumber', text_plumber))
                
                # Try pymupdf as fallback
                text_pymupdf = self._extract_with_pymupdf(pdf_path)
                results.append(('pymupdf', text_pymupdf))
                
                # Return the method with the most substantial text
                best_method, best_text = max(results, key=lambda x: self._score_text_quality(x[1]))
                print(f"Selected extraction method: {best_method}")
                return best_text
                
            elif method == 'pdfplumber':
                return self._extract_with_pdfplumber(pdf_path)
            elif method == 'pymupdf':
                return self._extract_with_pymupdf(pdf_path)
            else:
                return self._extract_with_pdfplumber(pdf_path)
                
        except Exception as e:
            print(f"Error in main extraction: {e}")
            return f"Error extracting text: {e}"
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber with table fallback"""
        try:
            full_text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages):
                    # Extract main text
                    text = page.extract_text() or ""
                    
                    # If text is minimal, try extracting from tables
                    if len(text.strip()) < 50:
                        tables = page.extract_tables()
                        table_text = self._extract_text_from_tables(tables)
                        if table_text:
                            text += "\n" + table_text
                    
                    # If still minimal, try with different extraction settings
                    if len(text.strip()) < 20:
                        text = page.extract_text_words() or ""
                        if text:
                            text = " ".join([word['text'] for word in text])
                    
                    if text and text.strip():
                        full_text += f"--- Page {page_num + 1} ---\n{text}\n\n"
            
            return full_text.strip()
            
        except Exception as e:
            print(f"Error in pdfplumber extraction: {e}")
            return ""
    
    def _extract_with_pymupdf(self, pdf_path: str) -> str:
        """Extract text using PyMuPDF (often better for complex layouts)"""
        try:
            full_text = ""
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract text with different methods
                text = page.get_text()
                
                # If standard extraction fails, try with different parameters
                if not text or len(text.strip()) < 20:
                    text = page.get_text("text", sort=True)
                
                if text and text.strip():
                    full_text += f"--- Page {page_num + 1} ---\n{text}\n\n"
            
            doc.close()
            return full_text.strip()
            
        except Exception as e:
            print(f"Error in PyMuPDF extraction: {e}")
            return ""
    
    def _extract_text_from_tables(self, tables: List) -> str:
        """Extract and format text from PDF tables"""
        if not tables:
            return ""
        
        text_lines = []
        for table_num, table in enumerate(tables):
            if table:  # Check if table is not empty
                for row_num, row in enumerate(table):
                    if row:  # Check if row is not None
                        # Filter out None values and clean cells
                        clean_row = [str(cell).strip() if cell is not None else "" for cell in row]
                        clean_row = [cell for cell in clean_row if cell]  # Remove empty strings
                        
                        if clean_row:  # Only add non-empty rows
                            row_text = " | ".join(clean_row)
                            text_lines.append(row_text)
                
                # Add separator between tables
                if text_lines and table_num < len(tables) - 1:
                    text_lines.append("---")
        
        return "\n".join(text_lines)
    
    def _score_text_quality(self, text: str) -> int:
        """Score text quality based on various factors"""
        if not text:
            return 0
        
        score = 0
        
        # Length score
        score += min(len(text) // 10, 100)  # Max 100 points for length
        
        # Structure score (presence of typical banking terms)
        banking_terms = ['date', 'description', 'amount', 'balance', 'debit', 'credit', 'withdrawal', 'deposit']
        for term in banking_terms:
            if term in text.lower():
                score += 5
        
        # Format score (presence of structured data patterns)
        import re
        if re.search(r'\d{1,2}[-/]\d{1,2}[-/]\d{2,4}', text):  # Date patterns
            score += 20
        if re.search(r'[₹$€]?\s*\d{1,3}(?:,\d{3})*\.?\d{0,2}', text):  # Currency patterns
            score += 20
        
        return score
    
    def extract_with_coordinates(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text with coordinates for advanced parsing and layout analysis"""
        try:
            text_blocks = []
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                blocks = page.get_text("dict")
                
                for block in blocks["blocks"]:
                    if "lines" in block:  # Text block
                        for line in block["lines"]:
                            for span in line["spans"]:
                                if span["text"].strip():  # Only non-empty text
                                    text_blocks.append({
                                        'page': page_num + 1,
                                        'text': span["text"],
                                        'bbox': span["bbox"],  # [x0, y0, x1, y1]
                                        'font': span["font"],
                                        'size': span["size"],
                                        'flags': span["flags"],
                                        'line_number': len(text_blocks) + 1
                                    })
            
            doc.close()
            return text_blocks
            
        except Exception as e:
            print(f"Error extracting text with coordinates: {e}")
            return []
    
    def get_extraction_stats(self, pdf_path: str) -> Dict[str, Any]:
        """Get statistics about the PDF extraction"""
        try:
            stats = {
                'total_pages': 0,
                'total_text_length': 0,
                'extraction_methods_tried': [],
                'success_rate': 0
            }
            
            # Try both methods
            text_plumber = self._extract_with_pdfplumber(pdf_path)
            text_pymupdf = self._extract_with_pymupdf(pdf_path)
            
            stats['extraction_methods_tried'] = ['pdfplumber', 'pymupdf']
            stats['pdfplumber_text_length'] = len(text_plumber)
            stats['pymupdf_text_length'] = len(text_pymupdf)
            stats['total_text_length'] = max(len(text_plumber), len(text_pymupdf))
            
            # Get page count
            try:
                with pdfplumber.open(pdf_path) as pdf:
                    stats['total_pages'] = len(pdf.pages)
            except:
                try:
                    doc = fitz.open(pdf_path)
                    stats['total_pages'] = len(doc)
                    doc.close()
                except:
                    stats['total_pages'] = 0
            
            # Calculate success rate
            if stats['total_pages'] > 0:
                avg_text_per_page = stats['total_text_length'] / stats['total_pages']
                stats['success_rate'] = min(100, (avg_text_per_page / 1000) * 100)  # Rough estimate
            
            return stats
            
        except Exception as e:
            print(f"Error getting extraction stats: {e}")
            return {}