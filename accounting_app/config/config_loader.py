import json
import os
from pathlib import Path
from .settings import get_config_path

class ConfigLoader:
    """Load and manage configuration files"""
    
    def __init__(self):
        self.categories = self._load_categories()
        self.account_mapping = self._load_account_mapping()
        self.bank_patterns = self._load_bank_patterns()
    
    def _load_categories(self):
        """Load categories configuration"""
        try:
            with open(get_config_path('categories.json'), 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: categories.json not found, using default categories")
            return self._get_default_categories()
        except json.JSONDecodeError as e:
            print(f"Error loading categories.json: {e}")
            return self._get_default_categories()
    
    def _load_account_mapping(self):
        """Load account mapping configuration"""
        try:
            with open(get_config_path('account_mapping.json'), 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: account_mapping.json not found, using default mapping")
            return self._get_default_account_mapping()
        except json.JSONDecodeError as e:
            print(f"Error loading account_mapping.json: {e}")
            return self._get_default_account_mapping()
    
    def _load_bank_patterns(self):
        """Load bank patterns configuration"""
        try:
            with open(get_config_path('bank_patterns.json'), 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: bank_patterns.json not found")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error loading bank_patterns.json: {e}")
            return {}
    
    def _get_default_categories(self):
        """Return default categories if config file is missing"""
        return {
            "income": {
                "keywords": ["donation", "salary", "refund", "interest", "neft", "imps", "upi credit"],
                "account_name": "Income Account",
                "type": "income"
            },
            "expense": {
                "keywords": ["snacks", "food", "printing", "stationery", "travel", "petrol"],
                "account_name": "Expense Account",
                "type": "expense"
            },
            "cash_withdrawal": {
                "keywords": ["atm", "cash", "withdrawal", "wdl"],
                "account_name": "Cash Account",
                "type": "transfer"
            }
        }
    
    def _get_default_account_mapping(self):
        """Return default account mapping if config file is missing"""
        return {
            "income": "To Income A/c",
            "expense": "To Expense A/c", 
            "cash_withdrawal": "To Cash A/c",
            "transfer": "To Bank Transfer A/c"
        }
    
    def get_category(self, category_name):
        """Get category configuration by name"""
        return self.categories.get(category_name)
    
    def get_all_categories(self):
        """Get all categories"""
        return self.categories
    
    def get_account_names(self, category_name):
        """Get debit and credit account names for a category"""
        category = self.get_category(category_name)
        if not category:
            return None
        
        account_type = category.get('type', 'expense')
        specific_account = self.account_mapping.get('specific_accounts', {}).get(category_name)
        
        if specific_account:
            return specific_account
        
        # Use account type template
        account_templates = self.account_mapping.get('account_types', {}).get(account_type, {})
        account_name = category.get('account_name', 'Miscellaneous')
        
        debit_account = account_templates.get('debit', '').format(account_name=account_name)
        credit_account = account_templates.get('credit', '').format(account_name=account_name)
        
        return {
            'debit': debit_account,
            'credit': credit_account
        }
    
    def find_category(self, description):
        """Find the best matching category for a description"""
        description_lower = description.lower()
        best_match = None
        best_score = 0
        
        for category_name, category_data in self.categories.items():
            keywords = category_data.get('keywords', [])
            score = 0
            
            for keyword in keywords:
                if keyword in description_lower:
                    score += 1
            
            if score > best_score:
                best_score = score
                best_match = category_name
        
        return best_match if best_match else 'miscellaneous'
    
    def get_bank_patterns(self, bank_name=None):
        """Get regex patterns for specific bank or generic patterns"""
        if bank_name and bank_name.lower() in self.bank_patterns:
            return self.bank_patterns[bank_name.lower()]
        return self.bank_patterns.get('generic', {})

# Create global config loader instance
config_loader = ConfigLoader()