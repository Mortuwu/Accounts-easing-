@echo off
chcp 65001
echo Building Bank Passbook to Accounting Converter...
echo.

echo Step 1: Checking Python...
python --version
if errorlevel 1 (
    echo ❌ Python not found or not in PATH
    goto :error
)

echo Step 2: Checking PyInstaller...
pyinstaller --version
if errorlevel 1 (
    echo ❌ PyInstaller not installed
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ Failed to install PyInstaller
        goto :error
    )
)

echo Step 3: Checking dependencies...
pip show streamlit >nul
if errorlevel 1 (
    echo ❌ Streamlit not installed
    goto :error
)

pip show pandas >nul
if errorlevel 1 (
    echo ❌ Pandas not installed
    goto :error
)

echo Step 4: Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "AccountingConverter.spec" del "AccountingConverter.spec"

echo Step 5: Building executable...
echo This may take several minutes...
pyinstaller --onefile --console ^
--name "AccountingConverter" ^
--add-data "main.py;." ^
--add-data "run_app.py;." ^
--add-data "config;config" ^
--add-data "pdf_processor;pdf_processor" ^
--add-data "parser;parser" ^
--add-data "categorizer;categorizer" ^
--add-data "journal;journal" ^
--add-data "exporter;exporter" ^
--add-data "utils;utils" ^
--hidden-import=streamlit ^
--hidden-import=pandas ^
--hidden-import=numpy ^
--hidden-import=pdfplumber ^
--hidden-import=pymupdf ^
--hidden-import=openpyxl ^
--hidden-import=reportlab ^
--hidden-import=sklearn ^
--hidden-import=joblib ^
accounting_app_launcher.py

if errorlevel 1 (
    echo ❌ Build failed!
    goto :error
)

echo Step 6: Checking build result...
if exist "dist\AccountingConverter.exe" (
    echo ✅ Build successful!
    echo.
    echo 📁 Executable location: dist\AccountingConverter.exe
    echo.
    echo 🚀 To run: double-click dist\AccountingConverter.exe
    echo.
    goto :success
) else (
    echo ❌ Executable not found in dist folder
    goto :error
)

:success
echo Build completed successfully!
pause
exit /b 0

:error
echo.
echo ❌ Build failed. Possible reasons:
echo 1. Missing dependencies - run: pip install -r requirements.txt
echo 2. PyInstaller issues - run: pip install --upgrade pyinstaller
echo 3. Antivirus blocking - temporarily disable during build
echo 4. Python path issues - check which Python is being used
echo.
pause
exit /b 1