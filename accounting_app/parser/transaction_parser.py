import pandas as pd
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from .regex_patterns import RegexPatterns
from .bank_format_detector import BankFormatDetector
from .amount_parser import AmountParser
from .date_parser import DateParser

class TransactionParser:
    def __init__(self, config_path=None):
        self.regex = RegexPatterns(config_path)
        self.bank_detector = BankFormatDetector()
        self.amount_parser = AmountParser()
        self.date_parser = DateParser()
        
        self.stats = {
            'total_lines_processed': 0,
            'transactions_found': 0,
            'bank_type_detected': None,
            'parsing_errors': 0
        }
    
    def parse_transactions(self, text: str, bank_type: str = "auto") -> pd.DataFrame:
        """
        Parse text into structured transactions with automatic bank detection
        """
        self._reset_stats()
        self.stats['total_lines_processed'] = len(text.split('\n'))
        
        # Detect bank type if auto
        if bank_type == "auto":
            bank_type = self.bank_detector.detect_bank_format(text)
            self.stats['bank_type_detected'] = bank_type
        
        # Find all transaction matches
        transaction_matches = self.regex.find_all_transactions(text, bank_type)
        self.stats['transactions_found'] = len(transaction_matches)
        
        # Parse each transaction
        transactions = []
        for match in transaction_matches:
            try:
                transaction = self._parse_transaction_match(match, bank_type)
                if transaction:
                    transactions.append(transaction)
            except Exception as e:
                self.stats['parsing_errors'] += 1
                print(f"Error parsing transaction: {e}")
        
        # Create DataFrame
        df = pd.DataFrame(transactions)
        
        # Sort by date if we have dates
        if not df.empty and 'date' in df.columns:
            df = self._sort_transactions(df)
        
        return df
    
    def _parse_transaction_match(self, match: tuple, bank_type: str) -> Optional[Dict[str, Any]]:
        """Parse a single transaction match into structured data"""
        if not match:
            return None
        
        try:
            # Handle different match lengths based on pattern
            if len(match) == 4:
                # Pattern: Date, Description, Amount, Type
                date_str, description, amount_str, type_str = match
                narration = ""
                transaction_code = ""
            elif len(match) == 5:
                # Pattern: Date, Description, Amount, Type, Narration
                date_str, description, amount_str, type_str, narration = match
                transaction_code = ""
            elif len(match) == 6:
                # Pattern: Date, Code, Description, Amount, Type, Narration
                date_str, transaction_code, description, amount_str, type_str, narration = match
            else:
                # Unknown pattern
                return None
            
            # Parse date
            date_obj = self.date_parser.parse_date(date_str)
            
            # Parse amount
            amount = self.amount_parser.parse_amount(amount_str)
            
            # Clean and normalize fields
            description = self._clean_description(description, transaction_code)
            type_str = type_str.upper()  # Normalize to uppercase
            narration = narration.strip()
            
            # Determine transaction category based on description
            category = self._categorize_transaction(description, type_str)
            
            transaction = {
                'date': date_obj if date_obj else date_str,
                'date_original': date_str,
                'description': description,
                'transaction_code': transaction_code,
                'amount': amount,
                'amount_original': amount_str,
                'type': type_str,
                'narration': narration,
                'category': category,
                'bank_type': bank_type,
                'original_match': str(match)
            }
            
            return transaction
            
        except Exception as e:
            self.stats['parsing_errors'] += 1
            print(f"Error parsing transaction match {match}: {e}")
            return None
    
    def _clean_description(self, description: str, transaction_code: str) -> str:
        """Clean and normalize transaction description"""
        if not description:
            return ""
        
        # Remove extra whitespace
        description = re.sub(r'\s+', ' ', description.strip())
        
        # Remove transaction code from description if it's already separate
        if transaction_code and transaction_code in description:
            description = description.replace(transaction_code, '').strip()
        
        # Clean common description patterns
        description = re.sub(r'^\s*[-*]\s*', '', description)  # Remove leading dashes/stars
        description = re.sub(r'\s*[-*]\s*$', '', description)  # Remove trailing dashes/stars
        
        return description
    
    def _categorize_transaction(self, description: str, transaction_type: str) -> str:
        """Simple categorization based on description keywords"""
        description_lower = description.lower()
        
        # Income-related keywords
        income_keywords = ['salary', 'interest', 'refund', 'donation', 'grant']
        if any(keyword in description_lower for keyword in income_keywords):
            return 'income'
        
        # Transfer keywords
        transfer_keywords = ['neft', 'imps', 'rtgs', 'upi', 'transfer']
        if any(keyword in description_lower for keyword in transfer_keywords):
            return 'transfer'
        
        # Cash withdrawal
        cash_keywords = ['atm', 'cash', 'withdrawal', 'wdl']
        if any(keyword in description_lower for keyword in cash_keywords):
            return 'cash_withdrawal'
        
        # Expense categories
        expense_keywords = {
            'food': ['restaurant', 'cafe', 'food', 'snacks', 'meal', 'lunch', 'dinner'],
            'transport': ['fuel', 'petrol', 'bus', 'train', 'taxi', 'uber', 'ola'],
            'shopping': ['market', 'store', 'shop', 'purchase', 'buy'],
            'utility': ['electricity', 'water', 'internet', 'mobile', 'bill']
        }
        
        for category, keywords in expense_keywords.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        # Default based on transaction type
        if transaction_type == 'CR':
            return 'income'
        else:
            return 'expense'
    
    def _sort_transactions(self, df: pd.DataFrame) -> pd.DataFrame:
        """Sort transactions by date"""
        try:
            # Convert to datetime for proper sorting
            df['date_temp'] = pd.to_datetime(df['date'], errors='coerce', dayfirst=True)
            df = df.sort_values('date_temp')
            df = df.drop('date_temp', axis=1)
        except:
            # Fallback: sort by original date string
            df = df.sort_values('date')
        
        return df.reset_index(drop=True)
    
    def _reset_stats(self):
        """Reset parsing statistics"""
        self.stats = {
            'total_lines_processed': 0,
            'transactions_found': 0,
            'bank_type_detected': None,
            'parsing_errors': 0
        }
    
    def get_parsing_stats(self) -> Dict[str, Any]:
        """Get parsing statistics"""
        return self.stats.copy()
    
    def validate_transaction(self, transaction: Dict[str, Any]) -> bool:
        """Validate if a parsed transaction has required fields"""
        required_fields = ['date', 'description', 'amount', 'type']
        
        for field in required_fields:
            if field not in transaction or not transaction[field]:
                return False
        
        # Validate amount is positive number
        try:
            amount = float(transaction['amount'])
            if amount <= 0:
                return False
        except:
            return False
        
        # Validate type is CR or DR
        if transaction['type'] not in ['CR', 'DR']:
            return False
        
        return True
    
    def parse_transactions_from_blocks(self, text_blocks: List[str], bank_type: str = "auto") -> pd.DataFrame:
        """
        Parse transactions from pre-extracted text blocks
        Useful when text cleaner has already identified transaction blocks
        """
        all_transactions = []
        
        for block in text_blocks:
            # Try to parse the entire block as a transaction
            transactions_df = self.parse_transactions(block, bank_type)
            if not transactions_df.empty:
                all_transactions.extend(transactions_df.to_dict('records'))
        
        return pd.DataFrame(all_transactions)