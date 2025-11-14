#!/usr/bin/env python3
"""
Bank Passbook to Accounting Converter - Executable Launcher
This file is the entry point for the PyInstaller executable
"""

import os
import sys
import subprocess
import webbrowser
import threading
import time
from pathlib import Path

def setup_environment():
    """Setup environment variables and paths for the executable"""
    
    # Get the base path (where the executable is located)
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        base_path = Path(sys.executable).parent
    else:
        # Running as script
        base_path = Path(__file__).parent
    
    # Add necessary paths
    config_path = base_path / "config"
    data_path = base_path / "data"
    exports_path = base_path / "exports"
    
    # Create directories if they don't exist
    for path in [config_path, data_path, exports_path]:
        path.mkdir(exist_ok=True)
    
    # Set up OCR paths for Windows
    if os.name == 'nt':  # Windows
        setup_windows_ocr_paths()
    
    return base_path

def setup_windows_ocr_paths():
    """Setup OCR paths for Windows executable"""
    try:
        # Common Tesseract installation paths
        tesseract_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            # Relative path for portable installation
            str(Path(__file__).parent / "tesseract" / "tesseract.exe")
        ]
        
        for path in tesseract_paths:
            if os.path.exists(path):
                os.environ['TESSERACT_CMD'] = path
                print(f"✅ Tesseract found: {path}")
                break
        else:
            print("⚠️ Tesseract not found. OCR functionality will be disabled.")
            print("   Please install Tesseract OCR for full functionality")
        
        # Poppler paths
        poppler_paths = [
            r"C:\poppler\Library\bin",
            r"C:\poppler\bin",
            str(Path(__file__).parent / "poppler" / "bin")
        ]
        
        for path in poppler_paths:
            if os.path.exists(path):
                os.environ['PATH'] = path + os.pathsep + os.environ['PATH']
                print(f"✅ Poppler found: {path}")
                break
        else:
            print("⚠️ Poppler not found. PDF to image conversion will be disabled.")
            print("   Please install Poppler for scanned PDF processing")
                
    except Exception as e:
        print(f"⚠️ Error setting up OCR paths: {e}")

def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import streamlit
    except ImportError:
        missing_deps.append("streamlit")
    
    try:
        import pandas
    except ImportError:
        missing_deps.append("pandas")
    
    try:
        import pdfplumber
    except ImportError:
        missing_deps.append("pdfplumber")
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Please install required packages:")
        print("pip install " + " ".join(missing_deps))
        return False
    
    return True

def open_browser():
    """Open browser after Streamlit starts"""
    time.sleep(3)  # Wait for Streamlit to start
    webbrowser.open("http://localhost:8501")

def main():
    """Main launcher function"""
    print("🏦 Bank Passbook to Accounting Converter")
    print("=" * 50)
    
    # Setup environment
    base_path = setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        print("❌ Cannot start application due to missing dependencies")
        input("Press Enter to exit...")
        return
    
    # Find the main app file
    main_app_path = base_path / "main.py"
    
    if not main_app_path.exists():
        print(f"❌ Main application file not found: {main_app_path}")
        input("Press Enter to exit...")
        return
    
    print("✅ Starting Accounting Converter...")
    print("📱 The application will open in your web browser")
    print("⚡ Server starting on http://localhost:8501")
    print("🛑 Press Ctrl+C in this window to stop the application")
    print("-" * 50)
    
    try:
        # Start browser in separate thread
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Start Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(main_app_path), 
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--browser.gatherUsageStats=false",
            "--theme.primaryColor=#366092",
            "--theme.backgroundColor=#ffffff",
            "--theme.secondaryBackgroundColor=#f0f2f6",
            "--theme.textColor=#262730"
        ])
        
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()  