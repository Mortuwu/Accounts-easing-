import pdfplumber
import fitz  # PyMuPDF
import os

class PDFDetector:
    def __init__(self):
        self.min_text_threshold = 100
        self.hybrid_threshold = 50
    
    def detect_pdf_type(self, pdf_path):
        """
        Detect if PDF is digital, scanned, or hybrid
        Returns: 'digital', 'scanned', or 'hybrid'
        """
        try:
            # Method 1: Try pdfplumber first
            text_length_plumber = self._check_with_pdfplumber(pdf_path)
            
            # Method 2: Try PyMuPDF for better text extraction
            text_length_pymupdf = self._check_with_pymupdf(pdf_path)
            
            # Method 3: Check if PDF contains images (for hybrid detection)
            has_images = self._check_for_images(pdf_path)
            
            # Determine PDF type based on results
            max_text_length = max(text_length_plumber, text_length_pymupdf)
            
            if max_text_length > self.min_text_threshold:
                if has_images and max_text_length < 500:  # Some text but also images
                    return 'hybrid'
                return 'digital'
            elif max_text_length > self.hybrid_threshold:
                return 'hybrid'
            else:
                return 'scanned'
                
        except Exception as e:
            print(f"Error detecting PDF type: {e}")
            return 'scanned'
    
    def _check_with_pdfplumber(self, pdf_path):
        """Extract text using pdfplumber"""
        try:
            text = ""
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text
            return len(text)
        except:
            return 0
    
    def _check_with_pymupdf(self, pdf_path):
        """Extract text using PyMuPDF (often better for some PDFs)"""
        try:
            text = ""
            doc = fitz.open(pdf_path)
            for page in doc:
                text += page.get_text()
            doc.close()
            return len(text)
        except:
            return 0
    
    def _check_for_images(self, pdf_path):
        """Check if PDF contains images"""
        try:
            doc = fitz.open(pdf_path)
            has_images = False
            for page in doc:
                image_list = page.get_images()
                if image_list:
                    has_images = True
                    break
            doc.close()
            return has_images
        except:
            return False
    
    def get_pdf_metadata(self, pdf_path):
        """Get PDF metadata like page count, creator, etc."""
        try:
            doc = fitz.open(pdf_path)
            metadata = {
                'page_count': len(doc),
                'author': doc.metadata.get('author', ''),
                'creator': doc.metadata.get('creator', ''),
                'producer': doc.metadata.get('producer', ''),
                'creation_date': doc.metadata.get('creationDate', ''),
                'file_size': os.path.getsize(pdf_path)
            }
            doc.close()
            return metadata
        except Exception as e:
            print(f"Error getting PDF metadata: {e}")
            return {}