import os
import tempfile
from .pdf_detector import PDFDetector
from .digital_extractor import DigitalExtractor
from .ocr_processor import OCRProcessor
from .text_cleaner import TextCleaner

class PDFManager:
    """
    Main coordinator for PDF processing
    Handles the complete pipeline from PDF to clean text
    """
    
    def __init__(self):
        self.detector = PDFDetector()
        self.digital_extractor = DigitalExtractor()
        self.ocr_processor = OCRProcessor()
        self.text_cleaner = TextCleaner()
        self.progress_callbacks = []
    
    def add_progress_callback(self, callback):
        """Add progress callback function"""
        self.progress_callbacks.append(callback)
    
    def _update_progress(self, stage, progress, message=""):
        """Update progress for all callbacks"""
        for callback in self.progress_callbacks:
            try:
                callback(stage, progress, message)
            except:
                pass
    
    def process_pdf(self, pdf_path, use_ocr_fallback=True):
        """
        Complete PDF processing pipeline
        Returns: dict with processed_text, pdf_type, metadata, and raw_text
        """
        result = {
            'processed_text': '',
            'pdf_type': 'unknown',
            'metadata': {},
            'raw_text': '',
            'success': False,
            'error': None
        }
        
        try:
            # Step 1: Detect PDF type
            self._update_progress('detection', 10, "Detecting PDF type...")
            pdf_type = self.detector.detect_pdf_type(pdf_path)
            result['pdf_type'] = pdf_type
            
            # Step 2: Extract text based on PDF type
            if pdf_type == 'digital':
                self._update_progress('extraction', 30, "Extracting digital text...")
                raw_text = self.digital_extractor.extract_text(pdf_path)
            else:
                self._update_progress('extraction', 30, "Converting PDF to images...")
                images = self.ocr_processor.pdf_to_images(pdf_path)
                
                self._update_progress('ocr', 60, "Performing OCR...")
                raw_text = self.ocr_processor.extract_text_from_images(images)
            
            result['raw_text'] = raw_text
            
            # Step 3: Clean extracted text
            self._update_progress('cleaning', 90, "Cleaning extracted text...")
            cleaned_text = self.text_cleaner.clean_extracted_text(raw_text)
            result['processed_text'] = cleaned_text
            
            # Step 4: Fallback to OCR if digital extraction failed
            if use_ocr_fallback and (not cleaned_text or len(cleaned_text.strip()) < 100):
                self._update_progress('fallback', 50, "Digital extraction failed, trying OCR...")
                images = self.ocr_processor.pdf_to_images(pdf_path)
                ocr_text = self.ocr_processor.extract_text_from_images(images)
                cleaned_ocr_text = self.text_cleaner.clean_extracted_text(ocr_text)
                
                if len(cleaned_ocr_text) > len(cleaned_text):
                    result['processed_text'] = cleaned_ocr_text
                    result['raw_text'] = ocr_text
                    result['pdf_type'] = 'scanned'
            
            result['success'] = len(result['processed_text'].strip()) > 0
            
            self._update_progress('complete', 100, "PDF processing complete!")
            
        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self._update_progress('error', 100, f"Error: {str(e)}")
        
        return result
    
    def process_pdf_file_object(self, file_object):
        """
        Process PDF from file object (like uploaded file in Streamlit)
        """
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(file_object.read())
            tmp_path = tmp_file.name
        
        try:
            result = self.process_pdf(tmp_path)
            return result
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    def validate_pdf(self, pdf_path):
        """Validate if PDF is processable"""
        try:
            # Check if file exists and is PDF
            if not os.path.exists(pdf_path):
                return False, "File does not exist"
            
            if not pdf_path.lower().endswith('.pdf'):
                return False, "File is not a PDF"
            
            # Try to open with pdfplumber
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                if len(pdf.pages) == 0:
                    return False, "PDF has no pages"
            
            return True, "PDF is valid"
        
        except Exception as e:
            return False, f"Invalid PDF: {str(e)}"