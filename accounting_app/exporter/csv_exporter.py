import pandas as pd
from typing import List, Dict, Any
import csv
import io

class CSVExporter:
    """Export data to CSV format with proper formatting"""
    
    def __init__(self):
        self.encoding = 'utf-8'
    
    def export_transactions_to_csv(self, transactions_df: pd.DataFrame, output_path: str) -> str:
        """Export transactions to CSV file"""
        try:
            # Create a copy to avoid modifying original
            export_df = transactions_df.copy()
            
            # Format dates
            if 'date' in export_df.columns:
                export_df['date'] = export_df['date'].apply(
                    lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else str(x)
                )
            
            # Format amounts
            if 'amount' in export_df.columns:
                export_df['amount'] = export_df['amount'].apply(
                    lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else str(x)
                )
            
            export_df.to_csv(output_path, index=False, encoding=self.encoding)
            print(f"Transactions exported to CSV: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error exporting transactions to CSV: {e}")
            raise
    
    def export_journal_to_csv(self, journal_entries: List[Dict[str, Any]], output_path: str) -> str:
        """Export journal entries to CSV file"""
        try:
            if not journal_entries:
                raise ValueError("No journal entries to export")
            
            # Convert to DataFrame
            journal_df = pd.DataFrame(journal_entries)
            
            # Format dates
            if 'date' in journal_df.columns:
                journal_df['date'] = journal_df['date'].apply(
                    lambda x: x.strftime('%d/%m/%Y') if hasattr(x, 'strftime') else str(x)
                )
            
            journal_df.to_csv(output_path, index=False, encoding=self.encoding)
            print(f"Journal entries exported to CSV: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error exporting journal entries to CSV: {e}")
            raise
    
    def export_to_csv_buffer(self, data: pd.DataFrame) -> bytes:
        """Export DataFrame to CSV bytes buffer"""
        try:
            output = io.StringIO()
            data.to_csv(output, index=False, encoding=self.encoding)
            return output.getvalue().encode(self.encoding)
        except Exception as e:
            print(f"Error creating CSV buffer: {e}")
            raise
    
    def export_multiple_sheets_to_csv(self, data_dict: Dict[str, pd.DataFrame], 
                                    output_dir: str, base_filename: str) -> List[str]:
        """Export multiple DataFrames to separate CSV files"""
        exported_files = []
        
        for sheet_name, df in data_dict.items():
            if df.empty:
                continue
                
            filename = f"{base_filename}_{sheet_name.lower().replace(' ', '_')}.csv"
            filepath = f"{output_dir}/{filename}"
            
            try:
                self.export_transactions_to_csv(df, filepath)
                exported_files.append(filepath)
            except Exception as e:
                print(f"Error exporting {sheet_name} to CSV: {e}")
        
        return exported_files