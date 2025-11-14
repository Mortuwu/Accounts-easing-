import os
import subprocess
import sys

def check_pyinstaller():
    """Check if PyInstaller is installed and working"""
    try:
        import PyInstaller
        print(f"✅ PyInstaller version: {PyInstaller.__version__}")
        return True
    except ImportError:
        print("❌ PyInstaller not installed")
        print("Run: pip install pyinstaller")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'streamlit', 'pandas', 'numpy', 'pdfplumber', 
        'pymupdf', 'openpyxl', 'reportlab'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"❌ {package}")
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("Run: pip install " + " ".join(missing))
        return False
    return True

def check_files():
    """Check if required files exist"""
    required_files = [
        'accounting_app_launcher.py',
        'main.py',
        'config/categories.json',
        'config/account_mapping.json'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            missing_files.append(file)
            print(f"❌ {file}")
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    return True

def test_pyinstaller_build():
    """Test a simple PyInstaller build"""
    print("\n🔨 Testing PyInstaller build...")
    
    # Create a simple test script
    test_script = """
print("Hello from PyInstaller test!")
input("Press Enter to exit...")
"""
    
    with open('test_build.py', 'w') as f:
        f.write(test_script)
    
    try:
        # Try to build the test script
        result = subprocess.run([
            'pyinstaller', '--onefile', 'test_build.py'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ PyInstaller build test successful!")
            if os.path.exists('dist/test_build.exe'):
                print("✅ Test executable created: dist/test_build.exe")
                return True
            else:
                print("❌ Test executable not found in dist/")
                return False
        else:
            print("❌ PyInstaller build failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running PyInstaller: {e}")
        return False
    finally:
        # Clean up test files
        if os.path.exists('test_build.py'):
            os.remove('test_build.py')

def main():
    print("🔍 PyInstaller Build Debugger")
    print("=" * 50)
    
    # Check PyInstaller
    if not check_pyinstaller():
        return
    
    print("\n📦 Checking dependencies...")
    if not check_dependencies():
        return
    
    print("\n📁 Checking required files...")
    if not check_files():
        return
    
    print("\n🧪 Testing PyInstaller...")
    test_pyinstaller_build()
    
    print("\n" + "=" * 50)
    print("Next steps:")
    print("1. If test build works, try the main build again")
    print("2. If test build fails, check PyInstaller installation")
    print("3. Run: pip install --upgrade pyinstaller")

if __name__ == "__main__":
    main()