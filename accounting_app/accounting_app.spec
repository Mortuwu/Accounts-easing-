# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['accounting_app_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include all Python files
        ('main.py', '.'),
        ('run_app.py', '.'),
        
        # Include config files
        ('config/*.json', 'config'),
        ('config/*.py', 'config'),
        
        # Include all module directories
        ('pdf_processor/*.py', 'pdf_processor'),
        ('parser/*.py', 'parser'),
        ('categorizer/*.py', 'categorizer'),
        ('journal/*.py', 'journal'),
        ('exporter/*.py', 'exporter'),
        ('utils/*.py', 'utils'),
    ],
    hiddenimports=[
        # Streamlit and web dependencies
        'streamlit',
        'streamlit.web',
        'streamlit.runtime',
        'streamlit.proto',
        
        # Data processing
        'pandas',
        'numpy',
        
        # PDF processing
        'pdfplumber',
        'pymupdf',
        'pdf2image',
        'pytesseract',
        'PIL',
        'PIL._imaging',
        'cv2',
        
        # Machine Learning
        'sklearn',
        'sklearn.ensemble',
        'sklearn.feature_extraction',
        'sklearn.utils',
        'joblib',
        
        # Export modules
        'openpyxl',
        'openpyxl.styles',
        'reportlab',
        'reportlab.lib',
        'reportlab.pdfgen',
        'fpdf2',
        
        # Utilities
        'dateutil',
        'pathlib',
        'json',
        're',
        'io',
        'tempfile',
        'base64',
        
        # Our custom modules
        'config.config_loader',
        'pdf_processor.pdf_manager',
        'parser.transaction_parser',
        'categorizer.category_manager',
        'journal.entry_generator',
        'exporter.excel_writer',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AccountingConverter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False if you don't want console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',  # Optional: add an icon file
)