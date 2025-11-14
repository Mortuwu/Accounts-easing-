import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter
import cv2
import numpy as np
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor

class OCRProcessor:
    def __init__(self, dpi=300, language='eng'):
        self.dpi = dpi
        self.language = language
        self.tesseract_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz/,.- '
    
    def pdf_to_images(self, pdf_path, first_page=None, last_page=None):
        """Convert PDF to images for OCR with page range support"""
        try:
            images = convert_from_path(
                pdf_path, 
                dpi=self.dpi,
                first_page=first_page,
                last_page=last_page,
                thread_count=4
            )
            return images
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
            return []
    
    def preprocess_image(self, image):
        """Enhance image for better OCR accuracy with multiple techniques"""
        # Convert PIL Image to OpenCV format
        img = np.array(image)
        
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        else:
            gray = img
        
        # Multiple preprocessing techniques
        processed_images = []
        
        # Technique 1: Simple threshold
        _, thresh1 = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        processed_images.append(('threshold', thresh1))
        
        # Technique 2: Adaptive threshold
        thresh2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 11, 2)
        processed_images.append(('adaptive', thresh2))
        
        # Technique 3: Otsu's threshold
        _, thresh3 = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed_images.append(('otsu', thresh3))
        
        # Return the best preprocessed image (we'll use adaptive for now)
        best_image = Image.fromarray(thresh2)
        
        # Enhance contrast and sharpness
        enhancer = ImageEnhance.Contrast(best_image)
        best_image = enhancer.enhance(2.0)
        
        enhancer = ImageEnhance.Sharpness(best_image)
        best_image = enhancer.enhance(2.0)
        
        return best_image
    
    def extract_text_from_image(self, image):
        """Perform OCR on a single image with multiple configurations"""
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Try different OCR configurations
            configs = [
                r'--oem 3 --psm 6',
                r'--oem 3 --psm 4',  # Single column of text
                r'--oem 3 --psm 3',  # Fully automatic page segmentation
            ]
            
            best_text = ""
            best_conf = 0
            
            for config in configs:
                try:
                    data = pytesseract.image_to_data(processed_image, config=config, output_type=pytesseract.Output.DICT)
                    
                    # Calculate average confidence
                    confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                    if confidences:
                        avg_confidence = sum(confidences) / len(confidences)
                        
                        # If this configuration gives better confidence, use it
                        if avg_confidence > best_conf:
                            best_conf = avg_confidence
                            # Re-extract text with this configuration
                            text = pytesseract.image_to_string(processed_image, config=config)
                            if len(text.strip()) > len(best_text.strip()):
                                best_text = text
                except:
                    continue
            
            # If no good configuration found, use default
            if not best_text.strip():
                best_text = pytesseract.image_to_string(processed_image, config=self.tesseract_config)
            
            return best_text.strip()
            
        except Exception as e:
            print(f"Error in OCR processing: {e}")
            return ""
    
    def extract_text_from_images(self, images):
        """Perform OCR on multiple images"""
        full_text = ""
        
        for i, image in enumerate(images):
            page_text = self.extract_text_from_image(image)
            full_text += f"--- Page {i + 1} ---\n{page_text}\n\n"
        
        return full_text
    
    def extract_text_parallel(self, images, max_workers=4):
        """Perform OCR on multiple images in parallel"""
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(self.extract_text_from_image, images))
        
        full_text = ""
        for i, page_text in enumerate(results):
            full_text += f"--- Page {i + 1} ---\n{page_text}\n\n"
        
        return full_text
    
    def get_ocr_confidence(self, image):
        """Get OCR confidence score for an image"""
        try:
            processed_image = self.preprocess_image(image)
            data = pytesseract.image_to_data(processed_image, output_type=pytesseract.Output.DICT)
            
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            if confidences:
                return sum(confidences) / len(confidences)
            return 0
        except:
            return 0