import json
from typing import Dict, Any, List

class AccountingRules:
    """
    Manages accounting rules and standards for journal entry generation
    Supports different accounting methods (cash, accrual) and standards
    """
    
    def __init__(self, rules_file: str = None):
        self.rules = self._load_rules(rules_file) if rules_file else self._get_default_rules()
        self.standards = {
            'ind_as': self._get_indian_accounting_standards(),
            'ifrs': self._get_ifrs_standards(),
            'gaap': self._get_gaap_standards()
        }
    
    def _load_rules(self, rules_file: str) -> Dict[str, Any]:
        """Load accounting rules from file"""
        try:
            with open(rules_file, 'r') as f:
                return json.load(f)
        except:
            return self._get_default_rules()
    
    def _get_default_rules(self) -> Dict[str, Any]:
        """Get default accounting rules"""
        return {
            "accounting_method": "cash",  # cash or accrual
            "currency": "INR",
            "rounding_method": "nearest",
            "decimal_places": 2,
            "date_format": "dd/mm/yyyy",
            "voucher_numbering": "auto",
            "narration_required": True,
            "auto_balance_check": True,
            "default_accounts": {
                "bank": "Bank Account",
                "cash": "Cash in Hand",
                "sales": "Sales Account",
                "purchase": "Purchase Account"
            }
        }
    
    def _get_indian_accounting_standards(self) -> Dict[str, Any]:
        """Get Indian Accounting Standards rules"""
        return {
            "name": "Indian Accounting Standards (Ind AS)",
            "revenue_recognition": "point_of_sale",
            "expense_recognition": "matching_principle",
            "inventory_valuation": "weighted_average",
            "depreciation_method": "straight_line"
        }
    
    def _get_ifrs_standards(self) -> Dict[str, Any]:
        """Get IFRS accounting standards"""
        return {
            "name": "International Financial Reporting Standards",
            "revenue_recognition": "transfer_of_control",
            "expense_recognition": "accrual_basis",
            "inventory_valuation": "first_in_first_out",
            "depreciation_method": "component"
        }
    
    def _get_gaap_standards(self) -> Dict[str, Any]:
        """Get GAAP accounting standards"""
        return {
            "name": "Generally Accepted Accounting Principles",
            "revenue_recognition": "realization_principle",
            "expense_recognition": "matching_principle",
            "inventory_valuation": "last_in_first_out",
            "depreciation_method": "multiple_methods"
        }
    
    def apply_standard(self, standard_name: str):
        """Apply specific accounting standard"""
        if standard_name.lower() in self.standards:
            self.rules.update(self.standards[standard_name.lower()])
    
    def validate_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Validate transaction against accounting rules"""
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ['date', 'description', 'amount', 'type']
        for field in required_fields:
            if field not in transaction or not transaction[field]:
                errors.append(f"Missing required field: {field}")
        
        # Validate amount
        if 'amount' in transaction:
            try:
                amount = float(transaction['amount'])
                if amount <= 0:
                    errors.append("Amount must be positive")
            except:
                errors.append("Invalid amount format")
        
        # Validate transaction type
        if 'type' in transaction and transaction['type'] not in ['CR', 'DR']:
            errors.append("Transaction type must be CR or DR")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }
    
    def get_account_suggestions(self, transaction_type: str, amount: float) -> List[str]:
        """Get account suggestions based on transaction type and amount"""
        suggestions = []
        
        if transaction_type == 'CR':  # Credit transactions
            if amount > 10000:
                suggestions.extend(['Donation Income', 'Grant Received', 'Loan Received'])
            else:
                suggestions.extend(['Service Income', 'Interest Income', 'Miscellaneous Income'])
        else:  # Debit transactions
            if amount < 1000:
                suggestions.extend(['Office Expenses', 'Travel Expenses', 'Communication Expenses'])
            else:
                suggestions.extend(['Equipment Purchase', 'Rent Payment', 'Salary Payment'])
        
        return suggestions