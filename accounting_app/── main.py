import streamlit as st
import pandas as pd
import tempfile
import os
import sys
from pathlib import Path

try:
    from config.ocr_config import setup_ocr_paths
    setup_ocr_paths()
except ImportError:
    print("⚠️ OCR config not found, proceeding without OCR setup")

# Test OCR functionality
def test_ocr():
    try:
        import pytesseract
        from PIL import Image
        print("✅ pytesseract imported successfully")
        
        # Test if tesseract command works
        try:
            pytesseract.get_tesseract_version()
            print("✅ Tesseract is working")
            return True
        except Exception as e:
            print(f"❌ Tesseract error: {e}")
            return False
            
    except ImportError as e:
        print(f"❌ OCR dependencies missing: {e}")
        return False

# Add the current directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent))

# Set page config first
st.set_page_config(
    page_title="Bank Passbook to Accounting Converter",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now import our modules
try:
    from pdf_processor.pdf_detector import PDFDetector
    from pdf_processor.digital_extractor import DigitalExtractor
    from pdf_processor.ocr_processor import OCRProcessor
    from pdf_processor.text_cleaner import TextCleaner
    from parser.transaction_parser import TransactionParser
    from categorizer.rule_engine import RuleEngine
    from journal.entry_generator import JournalEntryGenerator
    from exporter.excel_writer import ExcelWriter
    from exporter.pdf_generator import PDFGenerator
except ImportError as e:
    st.error(f"Module import error: {e}")
    st.info("Please make sure all module files are in the correct directories")

class AccountingApp:
    def __init__(self):
        """Initialize all processing components"""
        try:
            self.pdf_detector = PDFDetector()
            self.digital_extractor = DigitalExtractor()
            self.ocr_processor = OCRProcessor()
            self.text_cleaner = TextCleaner()
            self.parser = TransactionParser()
            self.categorizer = RuleEngine()
            self.journal_generator = JournalEntryGenerator()
            self.excel_writer = ExcelWriter()
            self.pdf_generator = PDFGenerator()
        except Exception as e:
            st.error(f"Error initializing app components: {e}")

    def process_pdf(self, pdf_file):
        """
        Main processing pipeline for PDF files
        Returns: (transactions_df, journal_entries, extracted_text)
        """
        # Save uploaded file to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_file.read())
            tmp_path = tmp_file.name

        transactions_df = None
        journal_entries = None
        extracted_text = ""

        try:
            # Step 1: Detect PDF type
            with st.spinner("🔍 Analyzing PDF type..."):
                pdf_type = self.pdf_detector.detect_pdf_type(tmp_path)
                st.success(f"Detected: **{pdf_type.upper()}** PDF")
                
                if pdf_type == 'scanned':
                    st.warning("⚠️ Scanned PDF detected - OCR processing may take longer")

            # Step 2: Extract text based on PDF type
            with st.spinner("📄 Extracting text from PDF..."):
                if pdf_type == 'digital':
                    raw_text = self.digital_extractor.extract_text(tmp_path)
                else:
                    images = self.ocr_processor.pdf_to_images(tmp_path)
                    if not images:
                        st.error("❌ Failed to convert PDF to images")
                        return None, None, ""
                    
                    progress_bar = st.progress(0)
                    raw_text = ""
                    total_pages = len(images)
                    
                    for i, image in enumerate(images):
                        page_text = self.ocr_processor.extract_text_from_image(image)
                        raw_text += f"--- Page {i+1} ---\n{page_text}\n\n"
                        progress_bar.progress((i + 1) / total_pages)
                
                # Clean the extracted text
                extracted_text = self.text_cleaner.clean_extracted_text(raw_text)
                
                # Show text preview
                with st.expander("📝 View Extracted Text (Preview)"):
                    st.text_area("Extracted Text", extracted_text[:2000] + "..." if len(extracted_text) > 2000 else extracted_text, height=200)

            # Step 3: Parse transactions
            with st.spinner("🔄 Parsing transactions..."):
                transactions_df = self.parser.parse_transactions(extracted_text)
                
                if transactions_df.empty:
                    st.error("❌ No transactions found in the extracted text!")
                    st.info("This could be because:")
                    st.info("- PDF format is not supported yet")
                    st.info("- OCR didn't work properly on scanned PDF")
                    st.info("- Transaction pattern not recognized")
                    return None, None, extracted_text
                
                st.success(f"✅ Successfully parsed **{len(transactions_df)}** transactions")

            # Step 4: Categorize transactions
            with st.spinner("🏷️ Categorizing transactions..."):
                transactions_df['category'] = transactions_df.apply(
                    lambda row: self.categorizer.categorize_transaction(
                        row['description'], row['amount'], row['type']
                    ), axis=1
                )

            # Step 5: Generate journal entries
            with st.spinner("📒 Generating journal entries..."):
                journal_entries = self.journal_generator.generate_all_entries(transactions_df)

            return transactions_df, journal_entries, extracted_text

        except Exception as e:
            st.error(f"❌ Error processing PDF: {str(e)}")
            return None, None, extracted_text
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass

def display_summary(transactions_df):
    """Display summary statistics"""
    if transactions_df is None or transactions_df.empty:
        return
    
    st.subheader("📊 Financial Summary")
    
    # Calculate metrics
    total_credit = transactions_df[transactions_df['type'] == 'CR']['amount'].sum()
    total_debit = transactions_df[transactions_df['type'] == 'DR']['amount'].sum()
    net_balance = total_credit - total_debit
    
    # Category breakdown
    category_summary = transactions_df.groupby('category').agg({
        'amount': 'sum',
        'type': 'count'
    }).rename(columns={'type': 'count'})
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Credit", f"₹{total_credit:,.2f}")
    with col2:
        st.metric("Total Debit", f"₹{total_debit:,.2f}")
    with col3:
        st.metric("Net Balance", f"₹{net_balance:,.2f}")
    with col4:
        st.metric("Total Transactions", len(transactions_df))
    
    # Category breakdown
    st.subheader("📈 Category Breakdown")
    col5, col6 = st.columns(2)
    
    with col5:
        st.write("**By Amount**")
        for category, data in category_summary.iterrows():
            st.write(f"- {category.title()}: ₹{data['amount']:,.2f}")
    
    with col6:
        st.write("**By Count**")
        for category, data in category_summary.iterrows():
            st.write(f"- {category.title()}: {data['count']} transactions")

def setup_sidebar():
    """Setup the sidebar with instructions"""
    st.sidebar.title("🏦 About")
    st.sidebar.markdown("""
    **Convert bank passbook PDFs to accounting journal entries automatically!**
    
    ### Supported PDF Types:
    - ✅ **Digital PDFs** (text selectable)
    - ✅ **Scanned PDFs** (OCR processing)
    - ✅ **Hybrid PDFs** (mixed content)
    
    ### How it works:
    1. Upload your bank passbook PDF
    2. System detects PDF type automatically
    3. Extracts and parses transactions
    4. Categorizes each transaction
    5. Generates accounting journal entries
    6. Export in multiple formats
    
    ### Supported Banks:
    - All major Indian banks (HDFC, SBI, ICICI, Axis, etc.)
    - Standard transaction formats
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.info("💡 **Tip**: For best results with scanned PDFs, ensure the image is clear and upright")

def main():
    """Main application function"""
    
    # Setup sidebar
    setup_sidebar()
    
    # Main header
    st.title("🏦 Bank Passbook to Accounting Converter")
    st.markdown("""
    Upload your bank passbook PDF and automatically convert transactions into proper accounting journal entries 
    with double-entry bookkeeping format.
    """)
    
    # File upload section
    st.subheader("📤 Upload Your Passbook PDF")
    uploaded_file = st.file_uploader(
        "Choose a PDF file", 
        type="pdf",
        help="Upload your bank statement or passbook in PDF format"
    )
    
    if uploaded_file is not None:
        # Display file info
        file_size = len(uploaded_file.getvalue()) / 1024  # KB
        st.info(f"📄 **File**: {uploaded_file.name} | **Size**: {file_size:.1f} KB")
        
        # Initialize app and process PDF
        app = AccountingApp()
        
        # Process the PDF
        transactions_df, journal_entries, extracted_text = app.process_pdf(uploaded_file)
        
        if transactions_df is not None and not transactions_df.empty:
            # Display results in tabs
            tab1, tab2, tab3, tab4 = st.tabs(["📋 Transactions", "📒 Journal Entries", "📊 Summary", "📤 Export"])
            
            with tab1:
                st.subheader("Parsed Transactions")
                st.dataframe(
                    transactions_df,
                    use_container_width=True,
                    height=400
                )
                
                # Show raw data
                with st.expander("View Raw Data"):
                    st.write(transactions_df.to_dict('records'))
            
            with tab2:
                st.subheader("Accounting Journal Entries")
                if journal_entries:
                    journal_df = pd.DataFrame(journal_entries)
                    st.dataframe(
                        journal_df,
                        use_container_width=True,
                        height=400
                    )
                    
                    # Display sample journal entries
                    st.subheader("Sample Journal Format")
                    if len(journal_entries) > 0:
                        sample_entry = journal_entries[0]
                        st.code(f"""
Date: {sample_entry['date']}
{sample_entry['debit']}
{sample_entry['credit']}
Narration: {sample_entry['narration']}
                        """, language=None)
                else:
                    st.warning("No journal entries generated")
            
            with tab3:
                display_summary(transactions_df)
            
            with tab4:
                st.subheader("Download Export Files")
                
                if transactions_df is not None and journal_entries is not None:
                    # Create temporary files for download
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        # Excel Export
                        try:
                            excel_buffer = app.excel_writer.export_to_excel_buffer(transactions_df, journal_entries)
                            st.download_button(
                                label="💾 Download Excel",
                                data=excel_buffer,
                                file_name="journal_entries.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                help="Download transactions and journal entries in Excel format"
                            )
                        except Exception as e:
                            st.error(f"Excel export error: {e}")
                    
                    with col2:
                        # PDF Export
                        try:
                            pdf_buffer = app.pdf_generator.generate_journal_pdf_buffer(journal_entries)
                            st.download_button(
                                label="📄 Download PDF",
                                data=pdf_buffer,
                                file_name="journal_entries.pdf",
                                mime="application/pdf",
                                help="Download journal entries in PDF format"
                            )
                        except Exception as e:
                            st.error(f"PDF export error: {e}")
                    
                    with col3:
                        # CSV Export
                        try:
                            csv_data = transactions_df.to_csv(index=False)
                            st.download_button(
                                label="📊 Download CSV",
                                data=csv_data,
                                file_name="transactions.csv",
                                mime="text/csv",
                                help="Download transactions in CSV format"
                            )
                        except Exception as e:
                            st.error(f"CSV export error: {e}")
                    
                    with col4:
                        # Raw Text Export
                        try:
                            st.download_button(
                                label="📝 Download Text",
                                data=extracted_text,
                                file_name="extracted_text.txt",
                                mime="text/plain",
                                help="Download raw extracted text from PDF"
                            )
                        except Exception as e:
                            st.error(f"Text export error: {e}")
                else:
                    st.warning("No data available for export")
        
        else:
            # Show error state
            st.error("❌ Failed to process the PDF file")
            
            # Debug information
            with st.expander("🔧 Debug Information"):
                if extracted_text:
                    st.text_area("Extracted Text for Analysis", extracted_text, height=300)
                else:
                    st.write("No text was extracted from the PDF")
                
                st.info("""
                **Common Issues:**
                - Scanned PDF with poor image quality
                - Unsupported bank statement format
                - PDF is password protected
                - Text orientation issues in scanned PDF
                
                **Next Steps:**
                - Try a different PDF file
                - Ensure scanned PDFs are clear and upright
                - Contact support for adding new bank formats
                """)

    else:
        # Show demo when no file is uploaded
        st.subheader("🎯 How to Use")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **1. Upload PDF**
            - Digital or scanned passbook
            - Any bank format
            """)
        
        with col2:
            st.markdown("""
            **2. Automatic Processing**
            - Text extraction
            - Transaction parsing
            - Smart categorization
            """)
        
        with col3:
            st.markdown("""
            **3. Export Results**
            - Excel files
            - PDF reports
            - CSV data
            """)
        
        # Sample data preview
        st.subheader("📋 Sample Output Preview")
        
        sample_transactions = pd.DataFrame({
            'date': ['15/03/2024', '16/03/2024', '17/03/2024'],
            'description': ['NEFT from John', 'ATM Cash Withdrawal', 'UPI Payment Restaurant'],
            'amount': [5000.00, 2000.00, 350.50],
            'type': ['CR', 'DR', 'DR'],
            'category': ['income', 'cash_withdrawal', 'expense']
        })
        
        st.dataframe(sample_transactions, use_container_width=True)

#import streamlit as st
import pandas as pd
import tempfile
import os
import sys
import json
import traceback
from datetime import datetime
from pathlib import Path

# Add the current directory to path so we can import our modules
sys.path.append(str(Path(__file__).parent))

# Set page config first (must be first Streamlit command)
st.set_page_config(
    page_title="Bank Passbook to Accounting Converter",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now import our modules
try:
    # PDF Processing
    from pdf_processor.pdf_manager import PDFManager
    
    # Parsing
    from parser.transaction_parser import TransactionParser
    from parser.bank_format_detector import BankFormatDetector
    
    # Categorization
    from categorizer.category_manager import CategoryManager
    
    # Journal Generation
    from journal.entry_generator import JournalEntryGenerator
    from journal.ledger_manager import LedgerManager
    
    # Export
    from exporter.excel_writer import ExcelWriter
    from exporter.pdf_generator import PDFGenerator
    from exporter.csv_exporter import CSVExporter
    from exporter.report_generator import ReportGenerator
    from exporter.tally_exporter import TallyExporter
    
except ImportError as e:
    st.error(f"❌ Module import error: {e}")
    st.info("Please make sure all module files are in the correct directories")
    st.stop()

class AccountingApp:
    def __init__(self):
        """Initialize all processing components with error handling"""
        try:
            # Initialize components
            self.pdf_manager = PDFManager()
            self.parser = TransactionParser()
            self.bank_detector = BankFormatDetector()
            self.category_manager = CategoryManager()
            self.journal_generator = JournalEntryGenerator()
            self.ledger_manager = LedgerManager()
            self.excel_writer = ExcelWriter()
            self.pdf_generator = PDFGenerator()
            self.csv_exporter = CSVExporter()
            self.report_generator = ReportGenerator()
            self.tally_exporter = TallyExporter()
            
            # Session state initialization
            self._init_session_state()
            
        except Exception as e:
            st.error(f"❌ Error initializing application: {e}")
            st.stop()
    
    def _init_session_state(self):
        """Initialize session state variables"""
        if 'processing_complete' not in st.session_state:
            st.session_state.processing_complete = False
        if 'transactions_df' not in st.session_state:
            st.session_state.transactions_df = None
        if 'journal_entries' not in st.session_state:
            st.session_state.journal_entries = None
        if 'extracted_text' not in st.session_state:
            st.session_state.extracted_text = ""
        if 'processing_stats' not in st.session_state:
            st.session_state.processing_stats = {}
        if 'current_file' not in st.session_state:
            st.session_state.current_file = None
    
    def process_pdf(self, pdf_file):
        """
        Main processing pipeline for PDF files
        
        Returns: (success, transactions_df, journal_entries, stats)
        """
        # Reset session state
        self._init_session_state()
        st.session_state.current_file = pdf_file.name
        
        # Save uploaded file to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_file.read())
            tmp_path = tmp_file.name
        
        try:
            # Initialize progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: PDF Processing (20%)
            status_text.text("🔍 Step 1/5: Analyzing and extracting PDF content...")
            pdf_result = self.pdf_manager.process_pdf(tmp_path)
            progress_bar.progress(20)
            
            if not pdf_result['success']:
                st.error(f"❌ PDF processing failed: {pdf_result.get('error', 'Unknown error')}")
                return False, None, None, {}
            
            st.session_state.extracted_text = pdf_result['processed_text']
            
            # Step 2: Transaction Parsing (40%)
            status_text.text("🔄 Step 2/5: Parsing transactions...")
            transactions_df = self.parser.parse_transactions(pdf_result['processed_text'])
            progress_bar.progress(40)
            
            if transactions_df.empty:
                st.error("❌ No transactions found in the extracted text!")
                return False, None, None, {}
            
            # Step 3: Bank Detection & Enhanced Parsing (50%)
            status_text.text("🏦 Step 3/5: Detecting bank format and enhancing data...")
            bank_type = self.bank_detector.detect_bank_format(pdf_result['processed_text'])
            parsing_stats = self.parser.get_parsing_stats()
            progress_bar.progress(50)
            
            # Step 4: Categorization (70%)
            status_text.text("🏷️ Step 4/5: Categorizing transactions...")
            transactions_df = self.category_manager.categorize_dataframe(transactions_df)
            categorization_stats = self.category_manager.get_category_analysis(transactions_df)
            progress_bar.progress(70)
            
            # Step 5: Journal Generation (90%)
            status_text.text("📒 Step 5/5: Generating accounting journal entries...")
            journal_entries = self.journal_generator.generate_all_entries(transactions_df)
            
            # Generate ledger
            self.ledger_manager.update_ledger(journal_entries)
            progress_bar.progress(90)
            
            # Validation (100%)
            status_text.text("✅ Validating results...")
            accounting_summary = self.journal_generator.get_accounting_summary(journal_entries)
            progress_bar.progress(100)
            
            # Update session state
            st.session_state.transactions_df = transactions_df
            st.session_state.journal_entries = journal_entries
            st.session_state.processing_complete = True
            
            # Compile processing statistics
            stats = {
                'pdf_type': pdf_result['pdf_type'],
                'bank_type': bank_type,
                'parsing_stats': parsing_stats,
                'categorization_stats': categorization_stats,
                'accounting_summary': accounting_summary,
                'file_metadata': pdf_result['metadata'],
                'processing_time': datetime.now().isoformat()
            }
            st.session_state.processing_stats = stats
            
            status_text.text("✅ Processing complete!")
            
            return True, transactions_df, journal_entries, stats
            
        except Exception as e:
            st.error(f"❌ Error during processing: {str(e)}")
            return False, None, None, {}
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
            except:
                pass
    
    def display_processing_summary(self, stats):
        """Display comprehensive processing summary"""
        st.subheader("📊 Processing Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("PDF Type", stats.get('pdf_type', 'Unknown').upper())
        with col2:
            st.metric("Bank Detected", stats.get('bank_type', 'Generic').upper())
        with col3:
            parsing_stats = stats.get('parsing_stats', {})
            st.metric("Transactions Found", parsing_stats.get('transactions_found', 0))
        with col4:
            cat_stats = stats.get('categorization_stats', {})
            st.metric("Categories Used", cat_stats.get('unique_categories', 0))
    
    def display_financial_summary(self, transactions_df):
        """Display financial summary and analytics"""
        st.subheader("💰 Financial Summary")
        
        if transactions_df is None or transactions_df.empty:
            st.warning("No transaction data available")
            return
        
        # Calculate key metrics
        total_credit = transactions_df[transactions_df['type'] == 'CR']['amount'].sum()
        total_debit = transactions_df[transactions_df['type'] == 'DR']['amount'].sum()
        net_balance = total_credit - total_debit
        total_transactions = len(transactions_df)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Credit", f"₹{total_credit:,.2f}")
        with col2:
            st.metric("Total Debit", f"₹{total_debit:,.2f}")
        with col3:
            st.metric("Net Balance", f"₹{net_balance:,.2f}")
        with col4:
            st.metric("Total Transactions", total_transactions)
        
        # Category breakdown
        if 'category' in transactions_df.columns:
            st.subheader("📈 Category Breakdown")
            
            col5, col6 = st.columns(2)
            
            with col5:
                st.write("**By Amount**")
                category_totals = transactions_df.groupby('category')['amount'].sum().sort_values(ascending=False)
                for category, amount in category_totals.items():
                    st.write(f"- {category.replace('_', ' ').title()}: ₹{amount:,.2f}")
            
            with col6:
                st.write("**By Count**")
                category_counts = transactions_df['category'].value_counts()
                for category, count in category_counts.items():
                    st.write(f"- {category.replace('_', ' ').title()}: {count} transactions")
    
    def setup_sidebar(self):
        """Setup the sidebar with instructions and controls"""
        st.sidebar.title("🏦 Accounting Converter")
        
        # App info
        st.sidebar.markdown("""
        **Convert bank passbook PDFs to accounting journal entries automatically!**
        
        ### Features:
        - ✅ **Digital PDFs** (text selectable)
        - ✅ **Scanned PDFs** (OCR processing)  
        - ✅ **Multiple Bank Formats** (HDFC, SBI, ICICI, Axis, etc.)
        - ✅ **Smart Categorization**
        - ✅ **Double-Entry Accounting**
        - ✅ **Multiple Export Formats**
        """)
        
        st.sidebar.markdown("---")
        
        # Processing options
        st.sidebar.subheader("⚙️ Processing Options")
        
        # AI Categorization toggle
        ai_enabled = st.sidebar.toggle("Enable AI Categorization", value=False)
        self.category_manager.set_ai_mode(ai_enabled)
        
        st.sidebar.markdown("---")
        
        # Instructions
        st.sidebar.subheader("📖 How to Use")
        st.sidebar.markdown("""
        1. **Upload** your bank passbook PDF
        2. **Wait** for automatic processing
        3. **Review** parsed transactions & journal entries
        4. **Export** in your preferred format
        
        **Supported Formats:**
        - Excel (.xlsx)
        - PDF Reports
        - CSV Data
        - Tally XML
        """)
    
    def export_data(self, transactions_df, journal_entries):
        """Handle all export functionality"""
        st.subheader("📤 Export Options")
        
        if transactions_df is None or journal_entries is None:
            st.warning("No data available for export")
            return
        
        # Create export tabs
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Excel", "📄 PDF", "📁 CSV", "🧮 Tally"])
        
        with tab1:
            self._export_excel(transactions_df, journal_entries)
        
        with tab2:
            self._export_pdf(journal_entries)
        
        with tab3:
            self._export_csv(transactions_df, journal_entries)
        
        with tab4:
            self._export_tally(journal_entries)
    
    def _export_excel(self, transactions_df, journal_entries):
        """Export to Excel format"""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("**Excel Export**")
            st.write("Professional Excel workbook with multiple sheets")
        
        with col2:
            if st.button("💾 Generate Excel File", key="excel_btn"):
                try:
                    with st.spinner("Creating Excel workbook..."):
                        excel_buffer = self.excel_writer.export_to_excel_buffer(
                            transactions_df, journal_entries
                        )
                    
                    st.download_button(
                        label="📥 Download Excel File",
                        data=excel_buffer,
                        file_name=f"accounting_journal_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key="excel_download"
                    )
                    
                except Exception as e:
                    st.error(f"Error generating Excel file: {e}")
    
    def _export_pdf(self, journal_entries):
        """Export to PDF format"""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("**PDF Report**")
            st.write("Professional PDF journal entries report")
        
        with col2:
            if st.button("📄 Generate PDF Report", key="pdf_btn"):
                try:
                    with st.spinner("Generating PDF report..."):
                        pdf_buffer = self.pdf_generator.generate_journal_pdf_buffer(journal_entries)
                    
                    st.download_button(
                        label="📥 Download PDF Report",
                        data=pdf_buffer,
                        file_name=f"journal_entries_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                        mime="application/pdf",
                        key="pdf_download"
                    )
                    
                except Exception as e:
                    st.error(f"Error generating PDF: {e}")
    
    def _export_csv(self, transactions_df, journal_entries):
        """Export to CSV format"""
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write("**CSV Export**")
            st.write("Simple CSV files for data interchange")
        
        with col2:
            transactions_csv = self.csv_exporter.export_to_csv_buffer(transactions_df)
            st.download_button(
                label="📥 Transactions CSV",
                data=transactions_csv,
                file_name=f"transactions_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                key="csv_transactions"
            )
        
        with col3:
            journal_df = pd.DataFrame(journal_entries)
            journal_csv = self.csv_exporter.export_to_csv_buffer(journal_df)
            st.download_button(
                label="📥 Journal Entries CSV",
                data=journal_csv,
                file_name=f"journal_entries_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                key="csv_journal"
            )
    
    def _export_tally(self, journal_entries):
        """Export to Tally format"""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.write("**Tally Export**")
            st.write("Tally accounting software compatible XML")
            
            company_name = st.text_input("Company Name for Tally", value="My Company")
        
        with col2:
            if st.button("🧮 Generate Tally XML", key="tally_btn"):
                try:
                    with st.spinner("Generating Tally XML..."):
                        tally_xml = self.tally_exporter.generate_tally_xml(
                            journal_entries, company_name
                        )
                    
                    st.download_button(
                        label="📥 Download Tally XML",
                        data=tally_xml,
                        file_name=f"tally_import_{datetime.now().strftime('%Y%m%d_%H%M')}.xml",
                        mime="application/xml",
                        key="tally_download"
                    )
                    
                except Exception as e:
                    st.error(f"Error generating Tally XML: {e}")

def main():
    """Main application function"""
    
    # Initialize application
    app = AccountingApp()
    
    # Setup sidebar
    app.setup_sidebar()
    
    # Main header
    st.title("🏦 Bank Passbook to Accounting Converter")
    st.markdown("""
    Automatically convert your bank passbook PDF transactions into professional accounting journal entries 
    with double-entry bookkeeping. Supports all major Indian banks and multiple export formats.
    """)
    
    # File upload section
    st.subheader("📤 Upload Your Passbook PDF")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file", 
        type="pdf",
        help="Upload your bank statement or passbook in PDF format",
        key="file_uploader"
    )
    
    if uploaded_file is not None:
        # Display file info
        file_size = len(uploaded_file.getvalue()) / 1024  # KB
        st.info(f"📄 **File**: {uploaded_file.name} | **Size**: {file_size:.1f} KB")
        
        # Process button
        if st.button("🚀 Process PDF", type="primary", key="process_btn"):
            # Process the PDF
            success, transactions_df, journal_entries, stats = app.process_pdf(uploaded_file)
            
            if success:
                st.success("✅ PDF processed successfully!")
                
                # Display processing summary
                app.display_processing_summary(stats)
                
                # Display financial summary
                app.display_financial_summary(transactions_df)
                
                # Display data in tabs
                tab1, tab2 = st.tabs(["📋 Transactions", "📒 Journal Entries"])
                
                with tab1:
                    st.subheader("Parsed Transactions")
                    if transactions_df is not None:
                        st.dataframe(
                            transactions_df,
                            use_container_width=True,
                            height=400
                        )
                    else:
                        st.warning("No transaction data available")
                
                with tab2:
                    st.subheader("Accounting Journal Entries")
                    if journal_entries:
                        journal_df = pd.DataFrame(journal_entries)
                        st.dataframe(
                            journal_df,
                            use_container_width=True,
                            height=400
                        )
                    else:
                        st.warning("No journal entries generated")
                
                # Export section
                st.markdown("---")
                app.export_data(transactions_df, journal_entries)
            
            else:
                st.error("❌ Failed to process the PDF file")
                
                # Debug information
                with st.expander("🔧 Debug Information"):
                    if st.session_state.extracted_text:
                        st.text_area("Extracted Text for Analysis", st.session_state.extracted_text, height=300)
                    else:
                        st.write("No text was extracted from the PDF")
    
    else:
        # Show demo when no file is uploaded
        st.subheader("🎯 How It Works")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **1. Upload PDF**
            - Digital or scanned passbook
            - Any bank format
            - Automatic type detection
            """)
        
        with col2:
            st.markdown("""
            **2. Automatic Processing**
            - Text extraction & OCR
            - Transaction parsing
            - Smart categorization
            - Journal generation
            """)
        
        with col3:
            st.markdown("""
            **3. Export & Analyze**
            - Excel workbooks
            - PDF reports  
            - CSV data
            - Tally XML
            """)
        
        # Sample data preview
        st.subheader("📋 Sample Output Preview")
        
        sample_transactions = pd.DataFrame({
            'date': ['15/03/2024', '16/03/2024', '17/03/2024'],
            'description': ['NEFT from John Doe', 'ATM Cash Withdrawal', 'UPI Payment - Restaurant'],
            'amount': [5000.00, 2000.00, 350.50],
            'type': ['CR', 'DR', 'DR'],
            'category': ['donation_income', 'cash_withdrawal', 'food_expense']
        })
        
        st.dataframe(sample_transactions, use_container_width=True)

if __name__ == "__main__":
    main()