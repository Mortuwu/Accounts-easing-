import os
import sys

def setup_ocr_paths():
    """Setup OCR paths for Windows"""
    
    # Tesseract paths
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    ]
    
    for path in tesseract_paths:
        if os.path.exists(path):
            os.environ['TESSERACT_CMD'] = path
            print(f"✅ Tesseract found: {path}")
            break
    else:
        print("❌ Tesseract not found. Please install from:")
        print("https://github.com/UB-Mannheim/tesseract/wiki")
    
    # Poppler paths
    poppler_paths = [
        r"C:\poppler\Library\bin",
        r"C:\poppler\bin"
    ]
    
    for path in poppler_paths:
        if os.path.exists(path):
            os.environ['PATH'] += os.pathsep + path
            print(f"✅ Poppler found: {path}")
            break
    else:
        print("❌ Poppler not found. Please install from:")
        print("https://github.com/oschwartz10612/poppler-windows/releases/")

# Run setup when module is imported
setup_ocr_paths()