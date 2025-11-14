@echo off
setlocal enabledelayedexpansion

echo Creating Portable Distribution...
echo.

echo Step 1: Building executable...
call build_exe.bat

echo.
echo Step 2: Creating portable distribution...
set DIST_DIR=Bank_Passbook_Converter_Portable
if exist "!DIST_DIR!" rmdir /s /q "!DIST_DIR!"
mkdir "!DIST_DIR!"

echo Copying executable...
xcopy "dist\AccountingConverter\*" "!DIST_DIR!\" /E /I /Y

echo Creating README...
echo Bank Passbook to Accounting Converter > "!DIST_DIR!\README.txt"
echo ===================================== >> "!DIST_DIR!\README.txt"
echo. >> "!DIST_DIR!\README.txt"
echo How to use: >> "!DIST_DIR!\README.txt"
echo 1. Double-click AccountingConverter.exe >> "!DIST_DIR!\README.txt"
echo 2. The application will open in your web browser >> "!DIST_DIR!\README.txt"
echo 3. Upload your bank passbook PDF to get started >> "!DIST_DIR!\README.txt"
echo. >> "!DIST_DIR!\README.txt"
echo For OCR functionality (scanned PDFs): >> "!DIST_DIR!\README.txt"
echo - Install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki >> "!DIST_DIR!\README.txt"
echo - Install Poppler from: https://github.com/oschwartz10612/poppler-windows/releases/ >> "!DIST_DIR!\README.txt"

echo Creating batch file for easy launch...
echo @echo off > "!DIST_DIR!\Run_Converter.bat"
echo echo Starting Bank Passbook Converter... >> "!DIST_DIR!\Run_Converter.bat"
echo AccountingConverter.exe >> "!DIST_DIR!\Run_Converter.bat"
echo pause >> "!DIST_DIR!\Run_Converter.bat"

echo.
echo ✅ Portable distribution created in: !DIST_DIR!\
echo.
echo 📦 Files included:
echo    - AccountingConverter.exe (Main application)
echo    - Run_Converter.bat (Easy launcher)
echo    - README.txt (Instructions)
echo    - config/ (Configuration files)
echo    - data/ (Data storage)
echo    - exports/ (Export files)
echo.
echo 🚀 To distribute:
echo    1. Zip the !DIST_DIR! folder
echo    2. Share the zip file
echo.
pause