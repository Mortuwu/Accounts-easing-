import json
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

class JournalEntryGenerator:
    def __init__(self, mapping_file: str = 'config/account_mapping.json'):
        self.account_mapping = self._load_account_mapping(mapping_file)
        self.accounting_rules = self._get_default_accounting_rules()
    
    def _load_account_mapping(self, mapping_file: str) -> Dict[str, Any]:
        """Load account mapping from JSON file"""
        try:
            file_path = Path(mapping_file)
            if not file_path.exists():
                return self._get_default_account_mapping()
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
                
        except Exception as e:
            print(f"Error loading account mapping: {e}")
            return self._get_default_accounting_rules()
    
    def _get_default_account_mapping(self) -> Dict[str, Any]:
        """Get default account mapping"""
        return {
            "account_types": {
                "income": {
                    "debit": "Bank Account",
                    "credit": "To {account_name}"
                },
                "expense": {
                    "debit": "{account_name}",
                    "credit": "To Bank Account"
                },
                "transfer": {
                    "debit": "{account_name}",
                    "credit": "To Bank Account"
                },
                "asset": {
                    "debit": "{account_name}",
                    "credit": "To Bank Account"
                },
                "liability": {
                    "debit": "{account_name}",
                    "credit": "To Bank Account"
                }
            },
            "specific_accounts": {
                "cash_withdrawal": {
                    "debit": "Cash Account",
                    "credit": "To Bank Account"
                },
                "bank_transfer": {
                    "debit": "Bank Transfer",
                    "credit": "To Bank Account"
                },
                "donation_income": {
                    "debit": "Bank Account",
                    "credit": "To Donation Income"
                },
                "salary_income": {
                    "debit": "Bank Account", 
                    "credit": "To Salary Income"
                },
                "food_expense": {
                    "debit": "Food Expense",
                    "credit": "To Bank Account"
                },
                "transport_expense": {
                    "debit": "Transport Expense",
                    "credit": "To Bank Account"
                }
            },
            "default_accounts": {
                "bank": "Bank Account",
                "cash": "Cash Account",
                "income": "Miscellaneous Income",
                "expense": "Miscellaneous Expense"
            }
        }
    
    def _get_default_accounting_rules(self) -> Dict[str, Any]:
        """Get default accounting rules"""
        return {
            "round_to_decimals": 2,
            "currency_symbol": "₹",
            "date_format": "%d/%m/%Y",
            "entry_format": "double_entry",
            "narration_style": "detailed"  # detailed, brief, minimal
        }
    
    def generate_journal_entry(self, transaction: Dict[str, Any], category: str) -> Dict[str, Any]:
        """
        Generate double-entry accounting journal entry
        
        Args:
            transaction: Transaction data with date, description, amount, type
            category: Transaction category
            
        Returns:
            Journal entry dictionary
        """
        date = transaction.get('date', '')
        description = transaction.get('description', '')
        amount = transaction.get('amount', 0)
        txn_type = transaction.get('type', 'DR').upper()
        
        # Format amount
        formatted_amount = self._format_amount(amount)
        
        # Get account names based on category and transaction type
        debit_account, credit_account = self._get_account_names(category, txn_type)
        
        # Generate narration
        narration = self._generate_narration(description, amount, txn_type)
        
        # Create journal entry
        if txn_type == 'CR':  # Credit to bank (money coming in)
            entry = {
                'date': date,
                'debit_account': debit_account,
                'debit_amount': formatted_amount,
                'credit_account': credit_account,
                'credit_amount': formatted_amount,
                'narration': narration,
                'type': 'credit',
                'transaction_type': txn_type,
                'category': category,
                'debit_entry': f"{debit_account} Dr {formatted_amount}",
                'credit_entry': f"To {credit_account} {formatted_amount}",
                'full_entry': f"{debit_account} Dr {formatted_amount}\nTo {credit_account} {formatted_amount}"
            }
        
        else:  # Debit from bank (money going out)
            entry = {
                'date': date,
                'debit_account': debit_account,
                'debit_amount': formatted_amount,
                'credit_account': credit_account,
                'credit_amount': formatted_amount,
                'narration': narration,
                'type': 'debit',
                'transaction_type': txn_type,
                'category': category,
                'debit_entry': f"{debit_account} Dr {formatted_amount}",
                'credit_entry': f"To {credit_account} {formatted_amount}",
                'full_entry': f"{debit_account} Dr {formatted_amount}\nTo {credit_account} {formatted_amount}"
            }
        
        return entry
    
    def _get_account_names(self, category: str, transaction_type: str) -> tuple:
        """Get debit and credit account names based on category and transaction type"""
        
        # Check specific account mappings first
        specific_accounts = self.account_mapping.get('specific_accounts', {})
        if category in specific_accounts:
            mapping = specific_accounts[category]
            return mapping['debit'], mapping['credit']
        
        # Get category type (income, expense, transfer, etc.)
        category_type = self._get_category_type(category)
        
        # Get account type template
        account_templates = self.account_mapping.get('account_types', {}).get(category_type, {})
        
        if transaction_type == 'CR':  # Money coming in
            debit_account = account_templates.get('debit', 'Bank Account')
            credit_account = account_templates.get('credit', 'To {account_name}').format(account_name=category.title())
        else:  # Money going out
            debit_account = account_templates.get('debit', '{account_name}').format(account_name=category.title())
            credit_account = account_templates.get('credit', 'To Bank Account')
        
        return debit_account, credit_account
    
    def _get_category_type(self, category: str) -> str:
        """Determine category type based on category name"""
        income_indicators = ['income', 'salary', 'donation', 'interest', 'refund']
        transfer_indicators = ['transfer', 'withdrawal', 'cash']
        
        category_lower = category.lower()
        
        if any(indicator in category_lower for indicator in income_indicators):
            return 'income'
        elif any(indicator in category_lower for indicator in transfer_indicators):
            return 'transfer'
        else:
            return 'expense'
    
    def _format_amount(self, amount: float) -> str:
        """Format amount with currency symbol"""
        currency_symbol = self.accounting_rules.get('currency_symbol', '₹')
        formatted = f"{amount:,.2f}"
        return f"{currency_symbol}{formatted}"
    
    def _generate_narration(self, description: str, amount: float, transaction_type: str) -> str:
        """Generate narration for journal entry"""
        style = self.accounting_rules.get('narration_style', 'detailed')
        currency_symbol = self.accounting_rules.get('currency_symbol', '₹')
        
        formatted_amount = f"{currency_symbol}{amount:,.2f}"
        
        if style == 'minimal':
            return description
        elif style == 'brief':
            return f"{description} - {formatted_amount}"
        else:  # detailed
            txn_type_desc = "Received" if transaction_type == 'CR' else "Paid"
            return f"{txn_type_desc} for {description} - Amount: {formatted_amount}"
    
    def generate_all_entries(self, transactions_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate journal entries for all transactions in DataFrame"""
        journal_entries = []
        
        for _, transaction in transactions_df.iterrows():
            category = transaction.get('category', 'miscellaneous')
            entry = self.generate_journal_entry(transaction.to_dict(), category)
            journal_entries.append(entry)
        
        return journal_entries
    
    def generate_ledger_summary(self, journal_entries: List[Dict[str, Any]]) -> Dict[str, float]:
        """Generate ledger account summary from journal entries"""
        ledger = {}
        
        for entry in journal_entries:
            # Process debit side
            debit_account = entry['debit_account']
            debit_amount = self._parse_amount(entry['debit_amount'])
            ledger[debit_account] = ledger.get(debit_account, 0) + debit_amount
            
            # Process credit side
            credit_account = entry['credit_account']
            credit_amount = self._parse_amount(entry['credit_amount'])
            ledger[credit_account] = ledger.get(credit_account, 0) - credit_amount
        
        return ledger
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float"""
        try:
            # Remove currency symbol and commas
            clean_amount = amount_str.replace('₹', '').replace(',', '')
            return float(clean_amount)
        except:
            return 0.0
    
    def export_journal_entries(self, journal_entries: List[Dict[str, Any]], 
                             format: str = 'dataframe') -> Any:
        """Export journal entries in different formats"""
        if format == 'dataframe':
            return pd.DataFrame(journal_entries)
        elif format == 'list':
            return journal_entries
        elif format == 'text':
            return self._format_entries_as_text(journal_entries)
        else:
            return journal_entries
    
    def _format_entries_as_text(self, journal_entries: List[Dict[str, Any]]) -> str:
        """Format journal entries as readable text"""
        text_output = "ACCOUNTING JOURNAL ENTRIES\n"
        text_output += "=" * 50 + "\n\n"
        
        for i, entry in enumerate(journal_entries, 1):
            text_output += f"Entry {i}:\n"
            text_output += f"Date: {entry['date']}\n"
            text_output += f"Debit:  {entry['debit_entry']}\n"
            text_output += f"Credit: {entry['credit_entry']}\n"
            text_output += f"Narration: {entry['narration']}\n"
            text_output += "-" * 40 + "\n\n"
        
        return text_output
    
    def validate_accounting_equation(self, journal_entries: List[Dict[str, Any]]) -> bool:
        """Validate that total debits equal total credits"""
        total_debits = 0
        total_credits = 0
        
        for entry in journal_entries:
            debit_amount = self._parse_amount(entry['debit_amount'])
            credit_amount = self._parse_amount(entry['credit_amount'])
            
            total_debits += debit_amount
            total_credits += credit_amount
        
        # Allow for small rounding differences
        return abs(total_debits - total_credits) < 0.01
    
    def get_accounting_summary(self, journal_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get accounting summary statistics"""
        total_debits = 0
        total_credits = 0
        entry_count = len(journal_entries)
        
        for entry in journal_entries:
            debit_amount = self._parse_amount(entry['debit_amount'])
            credit_amount = self._parse_amount(entry['credit_amount'])
            
            total_debits += debit_amount
            total_credits += credit_amount
        
        return {
            'total_entries': entry_count,
            'total_debits': total_debits,
            'total_credits': total_credits,
            'accounting_equation_balanced': self.validate_accounting_equation(journal_entries),
            'unique_accounts': len(self.generate_ledger_summary(journal_entries))
        }