import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from datetime import datetime

class TallyExporter:
    """Export data to Tally accounting software format"""
    
    def __init__(self):
        self.tally_version = "1.0"
        self.company_name = "Default Company"
    
    def generate_tally_xml(self, journal_entries: List[Dict[str, Any]], 
                          company_name: str = None) -> str:
        """
        Generate Tally-compatible XML for journal entries
        
        Args:
            journal_entries: List of journal entries
            company_name: Company name for Tally
            
        Returns:
            Tally XML as string
        """
        if company_name:
            self.company_name = company_name
        
        # Create XML structure
        root = ET.Element("ENVELOPE")
        
        # Header
        header = ET.SubElement(root, "HEADER")
        ET.SubElement(header, "TALLYREQUEST").text = "Import Data"
        
        # Body
        body = ET.SubElement(root, "BODY")
        data = ET.SubElement(body, "IMPORTDATA")
        request_desc = ET.SubElement(data, "REQUESTDESC")
        ET.SubElement(request_desc, "REPORTNAME").text = "Vouchers"
        
        # Company details
        company_data = ET.SubElement(data, "REQUESTDATA")
        tally_message = ET.SubElement(company_data, "TALLYMESSAGE", {"xmlns:UDF": "TallyUDF"})
        
        # Company creation
        company = ET.SubElement(tally_message, "COMPANY")
        ET.SubElement(company, "NAME").text = self.company_name
        
        # Add voucher entries
        for entry in journal_entries:
            voucher = self._create_voucher_element(tally_message, entry)
        
        # Convert to string
        xml_str = ET.tostring(root, encoding='unicode', method='xml')
        
        # Add XML declaration
        xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'
        return xml_declaration + '\n' + xml_str
    
    def _create_voucher_element(self, parent, entry: Dict[str, Any]) -> ET.Element:
        """Create Tally voucher element from journal entry"""
        voucher = ET.SubElement(parent, "VOUCHER")
        
        # Voucher details
        ET.SubElement(voucher, "DATE").text = self._format_date_for_tally(entry.get('date'))
        ET.SubElement(voucher, "NARRATION").text = entry.get('narration', '')[:100]  # Limit length
        
        # Voucher type (assuming all are journal vouchers)
        ET.SubElement(voucher, "VOUCHERTYPENAME").text = "Journal"
        
        # Debit entry
        debit_ledger = ET.SubElement(voucher, "ALLLEDGERENTRIES", {"LIST": "Debit"})
        ET.SubElement(debit_ledger, "LEDGERNAME").text = entry.get('debit_account', '')
        ET.SubElement(debit_ledger, "ISDEEMEDPOSITIVE").text = "No"  # Debit is positive
        ET.SubElement(debit_ledger, "AMOUNT").text = self._format_amount_for_tally(entry.get('debit_amount', 0))
        
        # Credit entry
        credit_ledger = ET.SubElement(voucher, "ALLLEDGERENTRIES", {"LIST": "Credit"})
        ET.SubElement(credit_ledger, "LEDGERNAME").text = entry.get('credit_account', '')
        ET.SubElement(credit_ledger, "ISDEEMEDPOSITIVE").text = "Yes"  # Credit is negative
        ET.SubElement(credit_ledger, "AMOUNT").text = self._format_amount_for_tally(entry.get('credit_amount', 0))
        
        return voucher
    
    def _format_date_for_tally(self, date_str: str) -> str:
        """Format date for Tally (YYYYMMDD)"""
        try:
            if hasattr(date_str, 'strftime'):
                return date_str.strftime('%Y%m%d')
            else:
                # Try to parse the date string
                for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d']:
                    try:
                        date_obj = datetime.strptime(str(date_str), fmt)
                        return date_obj.strftime('%Y%m%d')
                    except:
                        continue
                return datetime.now().strftime('%Y%m%d')
        except:
            return datetime.now().strftime('%Y%m%d')
    
    def _format_amount_for_tally(self, amount_str: str) -> str:
        """Format amount for Tally (remove currency symbol, handle formatting)"""
        try:
            if isinstance(amount_str, (int, float)):
                return str(amount_str)
            
            # Remove currency symbols and commas
            clean_amount = str(amount_str).replace('₹', '').replace(',', '').strip()
            return clean_amount
        except:
            return "0"
    
    def export_to_tally_file(self, journal_entries: List[Dict[str, Any]], 
                           output_path: str, company_name: str = None) -> str:
        """
        Export journal entries to Tally XML file
        
        Args:
            journal_entries: List of journal entries
            output_path: Output file path
            company_name: Company name for Tally
            
        Returns:
            Path to created file
        """
        try:
            tally_xml = self.generate_tally_xml(journal_entries, company_name)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(tally_xml)
            
            print(f"Tally XML exported: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error exporting to Tally XML: {e}")
            raise
    
    def validate_tally_compatibility(self, journal_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate journal entries for Tally compatibility"""
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'compatible_entries': 0
        }
        
        for i, entry in enumerate(journal_entries):
            entry_errors = []
            entry_warnings = []
            
            # Check required fields
            required_fields = ['date', 'debit_account', 'credit_account', 'debit_amount', 'credit_amount']
            for field in required_fields:
                if field not in entry or not entry[field]:
                    entry_errors.append(f"Missing required field: {field}")
            
            # Check amount consistency
            if 'debit_amount' in entry and 'credit_amount' in entry:
                try:
                    debit = float(str(entry['debit_amount']).replace('₹', '').replace(',', ''))
                    credit = float(str(entry['credit_amount']).replace('₹', '').replace(',', ''))
                    
                    if abs(debit - credit) > 0.01:  # Allow for rounding differences
                        entry_errors.append("Debit and credit amounts don't match")
                except:
                    entry_errors.append("Invalid amount format")
            
            # Check account name length (Tally has limits)
            if 'debit_account' in entry and len(entry['debit_account']) > 100:
                entry_warnings.append("Debit account name might be too long for Tally")
            
            if 'credit_account' in entry and len(entry['credit_account']) > 100:
                entry_warnings.append("Credit account name might be too long for Tally")
            
            # Check narration length
            if 'narration' in entry and len(entry['narration']) > 100:
                entry_warnings.append("Narration might be truncated in Tally")
            
            if not entry_errors:
                validation_result['compatible_entries'] += 1
            else:
                validation_result['is_valid'] = False
                validation_result['errors'].append({
                    'entry_index': i,
                    'errors': entry_errors
                })
            
            if entry_warnings:
                validation_result['warnings'].append({
                    'entry_index': i,
                    'warnings': entry_warnings
                })
        
        return validation_result