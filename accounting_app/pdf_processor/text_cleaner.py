import re
import string

class TextCleaner:
    def __init__(self):
        self.ocr_corrections = {
            # Common OCR mistakes
            '|': 'I', '0': 'O', '1': 'I', '5': 'S', '€': 'C', '£': 'E',
            '§': 'S', '©': 'C', '®': 'R', '™': 'TM', '¶': 'P',
            # Number and letter confusions
            'l': '1', 'O': '0', 'Z': '2', 'S': '5', 'G': '6', 'T': '7',
            'B': '8', 'q': '9', '£': 'E', '¥': 'Y'
        }
        
        self.bank_terms = {
            'NEFT': 'NEFT',
            'IMPS': 'IMPS', 
            'RTGS': 'RTGS',
            'UPI': 'UPI',
            'ATM': 'ATM',
            'CR': 'CR',
            'DR': 'DR',
            'IFSC': 'IFSC'
        }
    
    def clean_extracted_text(self, text):
        """Clean and normalize extracted text with multiple passes"""
        if not text:
            return ""
        
        # First pass: Basic cleaning
        text = self._basic_cleaning(text)
        
        # Second pass: Fix common OCR errors
        text = self._fix_ocr_errors(text)
        
        # Third pass: Bank-specific cleaning
        text = self._bank_specific_cleaning(text)
        
        # Fourth pass: Structure improvement
        text = self._improve_structure(text)
        
        return text.strip()
    
    def _basic_cleaning(self, text):
        """Perform basic text cleaning"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix line breaks in the middle of words
        text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
        
        # Remove special characters but keep essential ones
        text = re.sub(r'[^\w\s\/\-\.\,\:\;\(\)\&\@\#\$\*]', '', text)
        
        # Fix multiple spaces
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    def _fix_ocr_errors(self, text):
        """Fix common OCR mistakes"""
        # Apply character replacements
        for wrong, correct in self.ocr_corrections.items():
            text = text.replace(wrong, correct)
        
        # Fix common word errors
        common_errors = {
            'rn': 'm',
            'cl': 'd',
            'vv': 'w',
            'ii': 'n',
            'ij': 'h',
            '1o': '10',
            'lO': '10'
        }
        
        for error, correction in common_errors.items():
            text = text.replace(error, correction)
        
        return text
    
    def _bank_specific_cleaning(self, text):
        """Clean and standardize bank-specific terms"""
        # Standardize bank transaction types
        text = re.sub(r'(?i)\b(neft|NEFT|NefT)\b', 'NEFT', text)
        text = re.sub(r'(?i)\b(imps|IMPS|ImpS)\b', 'IMPS', text)
        text = re.sub(r'(?i)\b(rtgs|RTGS|RtgS)\b', 'RTGS', text)
        text = re.sub(r'(?i)\b(upi|UPI|UpI)\b', 'UPI', text)
        text = re.sub(r'(?i)\b(atm|ATM|AtM)\b', 'ATM', text)
        
        # Standardize CR/DR
        text = re.sub(r'(?i)\b(cr|CR|Cr)\b', 'CR', text)
        text = re.sub(r'(?i)\b(dr|DR|Dr)\b', 'DR', text)
        
        # Fix date formats
        text = re.sub(r'(\d{1,2})[\.\-\s](\d{1,2})[\.\-\s](\d{2,4})', r'\1/\2/\3', text)
        
        # Fix amount formats
        text = re.sub(r'(\d{1,3}),(\d{3}),(\d{3})', r'\1,\2\3', text)  # Fix extra commas
        text = re.sub(r'(\d),(\d{3})', r'\1\2', text)  # Remove commas in amounts
        
        return text
    
    def _improve_structure(self, text):
        """Improve text structure for better parsing"""
        # Ensure proper line breaks for transaction lines
        lines = text.split('\n')
        cleaned_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line:
                i += 1
                continue
            
            # Check if this looks like the start of a transaction (date pattern)
            if re.match(r'\d{1,2}/\d{1,2}/\d{2,4}', line):
                # This might be a complete transaction line
                cleaned_lines.append(line)
            else:
                # This might be a continuation, append to previous line
                if cleaned_lines:
                    cleaned_lines[-1] += " " + line
                else:
                    cleaned_lines.append(line)
            
            i += 1
        
        return '\n'.join(cleaned_lines)
    
    def extract_transaction_blocks(self, text):
        """Extract potential transaction blocks from text"""
        lines = text.split('\n')
        transaction_blocks = []
        current_block = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if line contains transaction indicators
            has_date = re.search(r'\d{1,2}/\d{1,2}/\d{2,4}', line)
            has_amount = re.search(r'[\d,]+\.?\d*\s*(CR|DR)', line, re.IGNORECASE)
            
            if has_date and has_amount:
                # This looks like a transaction line
                if current_block:
                    transaction_blocks.append(' '.join(current_block))
                    current_block = []
                transaction_blocks.append(line)
            elif has_date or has_amount:
                # Might be part of a transaction
                current_block.append(line)
            elif current_block:
                # Continue current block
                current_block.append(line)
            else:
                # Standalone line, add as separate block
                transaction_blocks.append(line)
        
        # Add the last block if exists
        if current_block:
            transaction_blocks.append(' '.join(current_block))
        
        return transaction_blocks
    
    def remove_header_footer(self, text, header_lines=3, footer_lines=2):
        """Remove header and footer lines"""
        lines = text.split('\n')
        
        if len(lines) <= header_lines + footer_lines:
            return text
        
        # Remove header and footer
        cleaned_lines = lines[header_lines:-footer_lines] if footer_lines > 0 else lines[header_lines:]
        
        return '\n'.join(cleaned_lines)
    
    def normalize_dates(self, text, target_format='%d/%m/%Y'):
        """Normalize date formats in text"""
        # This is a placeholder for date normalization
        # In practice, you'd want to parse and reformat dates
        return text