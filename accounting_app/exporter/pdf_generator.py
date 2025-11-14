from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.pdfgen import canvas
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from typing import List, Dict, Any, Optional
import pandas as pd
from datetime import datetime
import os
import io

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
        self.page_size = A4
    
    def _create_custom_styles(self):
        """Create custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=1  # Center
        ))
        
        # Header style
        self.styles.add(ParagraphStyle(
            name='CustomHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=20
        ))
        
        # Normal style
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=6
        ))
    
    def generate_journal_pdf(self, journal_entries: List[Dict[str, Any]], output_path: str, 
                           title: str = "Accounting Journal Entries") -> str:
        """
        Generate professional PDF with journal entries
        
        Args:
            journal_entries: List of journal entries
            output_path: Output file path
            title: Report title
            
        Returns:
            Path to created PDF
        """
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=self.page_size,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            elements = []
            
            # Add title
            title_para = Paragraph(title, self.styles['CustomTitle'])
            elements.append(title_para)
            elements.append(Spacer(1, 0.2*inch))
            
            # Add generation date
            date_para = Paragraph(f"Generated on: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 
                                self.styles['CustomNormal'])
            elements.append(date_para)
            elements.append(Spacer(1, 0.3*inch))
            
            # Create journal entries table
            if journal_entries:
                table_data = self._prepare_journal_table_data(journal_entries)
                journal_table = Table(table_data, colWidths=[1*inch, 2.5*inch, 2.5*inch, 3*inch])
                journal_table.setStyle(self._get_journal_table_style())
                elements.append(journal_table)
            else:
                no_data_para = Paragraph("No journal entries available", self.styles['CustomNormal'])
                elements.append(no_data_para)
            
            # Add summary
            elements.append(Spacer(1, 0.3*inch))
            summary_para = Paragraph("Summary", self.styles['CustomHeader'])
            elements.append(summary_para)
            
            summary_data = self._generate_summary_data(journal_entries)
            summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
            summary_table.setStyle(self._get_summary_table_style())
            elements.append(summary_table)
            
            # Build PDF
            doc.build(elements, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
            
            print(f"PDF generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            raise
    
    def generate_comprehensive_report(self, transactions_df: pd.DataFrame, 
                                    journal_entries: List[Dict[str, Any]], 
                                    output_path: str) -> str:
        """
        Generate comprehensive financial report PDF
        """
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=self.page_size,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            elements = []
            
            # Title page
            elements.extend(self._create_title_page())
            elements.append(Spacer(1, 0.5*inch))
            
            # Table of Contents
            elements.extend(self._create_table_of_contents())
            elements.append(Spacer(1, 0.5*inch))
            
            # Executive Summary
            elements.extend(self._create_executive_summary(transactions_df, journal_entries))
            elements.append(Spacer(1, 0.3*inch))
            
            # Transactions Summary
            if not transactions_df.empty:
                elements.extend(self._create_transactions_section(transactions_df))
                elements.append(Spacer(1, 0.3*inch))
            
            # Journal Entries
            if journal_entries:
                elements.extend(self._create_journal_section(journal_entries))
                elements.append(Spacer(1, 0.3*inch))
            
            # Financial Analysis
            elements.extend(self._create_analysis_section(transactions_df))
            
            # Build PDF with page numbers
            doc.build(elements, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
            
            print(f"Comprehensive report generated: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error generating comprehensive report: {e}")
            raise
    
    def _create_title_page(self) -> List[Any]:
        """Create title page elements"""
        elements = []
        
        # Main title
        title_style = ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=1
        )
        
        elements.append(Paragraph("FINANCIAL TRANSACTION REPORT", title_style))
        elements.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        subtitle_style = ParagraphStyle(
            name='ReportSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#7f8c8d'),
            spaceAfter=20,
            alignment=1
        )
        
        elements.append(Paragraph("Bank Passbook to Accounting Conversion", subtitle_style))
        elements.append(Spacer(1, 1*inch))
        
        # Generation info
        info_style = ParagraphStyle(
            name='ReportInfo',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#34495e'),
            alignment=1
        )
        
        elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}", info_style))
        elements.append(Paragraph("Automated Accounting System", info_style))
        
        return elements
    
    def _create_table_of_contents(self) -> List[Any]:
        """Create table of contents"""
        elements = []
        
        elements.append(Paragraph("Table of Contents", self.styles['CustomHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        toc_items = [
            "1. Executive Summary",
            "2. Transactions Overview", 
            "3. Journal Entries",
            "4. Financial Analysis",
            "5. Category Breakdown"
        ]
        
        for item in toc_items:
            elements.append(Paragraph(item, self.styles['CustomNormal']))
        
        return elements
    
    def _create_executive_summary(self, transactions_df: pd.DataFrame, 
                                journal_entries: List[Dict[str, Any]]) -> List[Any]:
        """Create executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['CustomHeader']))
        
        # Calculate summary statistics
        total_transactions = len(transactions_df) if not transactions_df.empty else 0
        total_credit = transactions_df[transactions_df['type'] == 'CR']['amount'].sum() if not transactions_df.empty else 0
        total_debit = transactions_df[transactions_df['type'] == 'DR']['amount'].sum() if not transactions_df.empty else 0
        net_balance = total_credit - total_debit
        journal_count = len(journal_entries)
        
        summary_text = f"""
        This report summarizes {total_transactions} financial transactions converted into 
        {journal_count} accounting journal entries. The analysis covers a total credit amount 
        of ₹{total_credit:,.2f} and debit amount of ₹{total_debit:,.2f}, resulting in a net 
        balance of ₹{net_balance:,.2f}.
        """
        
        elements.append(Paragraph(summary_text, self.styles['CustomNormal']))
        
        return elements
    
    def _create_transactions_section(self, transactions_df: pd.DataFrame) -> List[Any]:
        """Create transactions overview section"""
        elements = []
        
        elements.append(Paragraph("Transactions Overview", self.styles['CustomHeader']))
        
        # Create summary table
        summary_data = [['Metric', 'Value']]
        
        if not transactions_df.empty:
            credit_count = len(transactions_df[transactions_df['type'] == 'CR'])
            debit_count = len(transactions_df[transactions_df['type'] == 'DR'])
            total_amount = transactions_df['amount'].sum()
            
            summary_data.extend([
                ['Total Transactions', str(len(transactions_df))],
                ['Credit Transactions', str(credit_count)],
                ['Debit Transactions', str(debit_count)],
                ['Total Amount', f"₹{total_amount:,.2f}"]
            ])
        
        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(summary_table)
        
        return elements
    
    def _create_journal_section(self, journal_entries: List[Dict[str, Any]]) -> List[Any]:
        """Create journal entries section"""
        elements = []
        
        elements.append(Paragraph("Journal Entries", self.styles['CustomHeader']))
        
        # Create simplified journal table (first 10 entries for preview)
        preview_entries = journal_entries[:10]
        table_data = self._prepare_journal_table_data(preview_entries)
        
        if len(journal_entries) > 10:
            elements.append(Paragraph(f"Showing first 10 of {len(journal_entries)} entries", 
                                    self.styles['CustomNormal']))
        
        journal_table = Table(table_data, colWidths=[1*inch, 2*inch, 2*inch, 3*inch])
        journal_table.setStyle(self._get_journal_table_style())
        elements.append(journal_table)
        
        return elements
    
    def _create_analysis_section(self, transactions_df: pd.DataFrame) -> List[Any]:
        """Create financial analysis section"""
        elements = []
        
        elements.append(Paragraph("Financial Analysis", self.styles['CustomHeader']))
        
        if transactions_df.empty or 'category' not in transactions_df.columns:
            elements.append(Paragraph("No category data available for analysis", 
                                    self.styles['CustomNormal']))
            return elements
        
        # Category analysis
        category_totals = transactions_df.groupby('category')['amount'].sum().reset_index()
        category_totals = category_totals.sort_values('amount', ascending=False)
        
        elements.append(Paragraph("Category-wise Summary", self.styles['Heading3']))
        
        # Create category table
        category_data = [['Category', 'Total Amount']]
        for _, row in category_totals.iterrows():
            category_data.append([row['category'], f"₹{row['amount']:,.2f}"])
        
        category_table = Table(category_data, colWidths=[3*inch, 2*inch])
        category_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        elements.append(category_table)
        
        return elements
    
    def _prepare_journal_table_data(self, journal_entries: List[Dict[str, Any]]) -> List[List[str]]:
        """Prepare journal entries data for table"""
        table_data = [['Date', 'Debit Account', 'Credit Account', 'Narration']]
        
        for entry in journal_entries:
            # Format date
            date_str = entry.get('date', '')
            if hasattr(date_str, 'strftime'):
                date_str = date_str.strftime('%d/%m/%Y')
            
            table_data.append([
                str(date_str),
                entry.get('debit_account', ''),
                entry.get('credit_account', ''),
                entry.get('narration', '')[:50] + '...' if len(entry.get('narration', '')) > 50 else entry.get('narration', '')
            ])
        
        return table_data
    
    def _get_journal_table_style(self) -> TableStyle:
        """Get table style for journal entries"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ])
    
    def _get_summary_table_style(self) -> TableStyle:
        """Get table style for summary data"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#d5f4e6')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ])
    
    def _generate_summary_data(self, journal_entries: List[Dict[str, Any]]) -> List[List[str]]:
        """Generate summary data for PDF"""
        summary_data = [
            ['Total Journal Entries', str(len(journal_entries))],
            ['Report Type', 'Accounting Journal'],
            ['Format', 'Double Entry'],
            ['Status', 'Completed']
        ]
        return summary_data
    
    def _add_header_footer(self, canvas: canvas.Canvas, doc):
        """Add header and footer to PDF pages"""
        canvas.saveState()
        
        # Header
        canvas.setFont('Helvetica-Bold', 12)
        canvas.setFillColor(colors.HexColor('#2c3e50'))
        canvas.drawString(doc.leftMargin, doc.pagesize[1] - 0.5*inch, "Financial Transaction Report")
        
        # Footer
        canvas.setFont('Helvetica', 9)
        canvas.setFillColor(colors.HexColor('#7f8c8d'))
        page_num = canvas.getPageNumber()
        canvas.drawString(doc.leftMargin, 0.5*inch, f"Page {page_num}")
        canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 0.5*inch, 
                             f"Generated on {datetime.now().strftime('%d/%m/%Y')}")
        
        canvas.restoreState()
    
    def generate_journal_pdf_buffer(self, journal_entries: List[Dict[str, Any]]) -> bytes:
        """Generate PDF and return as bytes buffer"""
        import tempfile
        import io
        
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                self.generate_journal_pdf(journal_entries, tmp_file.name)
                
                # Read the file back into memory
                with open(tmp_file.name, 'rb') as f:
                    pdf_buffer = io.BytesIO(f.read())
                
                # Clean up
                os.unlink(tmp_file.name)
                
                return pdf_buffer.getvalue()
                
        except Exception as e:
            print(f"Error creating PDF buffer: {e}")
            raise