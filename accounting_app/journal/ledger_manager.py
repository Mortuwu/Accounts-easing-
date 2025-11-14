import pandas as pd
from typing import Dict, List, Any
from datetime import datetime

class LedgerManager:
    """
    Manages ledger accounts and generates ledger reports
    """
    
    def __init__(self):
        self.ledger_accounts = {}
        self.opening_balances = {}
    
    def set_opening_balance(self, account_name: str, balance: float):
        """Set opening balance for an account"""
        self.opening_balances[account_name] = balance
    
    def update_ledger(self, journal_entries: List[Dict[str, Any]]):
        """Update ledger accounts from journal entries"""
        for entry in journal_entries:
            self._process_journal_entry(entry)
    
    def _process_journal_entry(self, entry: Dict[str, Any]):
        """Process a single journal entry into ledger accounts"""
        date = entry['date']
        debit_account = entry['debit_account']
        credit_account = entry['credit_account']
        amount = self._parse_amount(entry['debit_amount'])
        narration = entry['narration']
        
        # Process debit account
        if debit_account not in self.ledger_accounts:
            self.ledger_accounts[debit_account] = []
        
        self.ledger_accounts[debit_account].append({
            'date': date,
            'particulars': f"To {credit_account}",
            'debit': amount,
            'credit': 0,
            'narration': narration,
            'type': 'debit'
        })
        
        # Process credit account
        if credit_account not in self.ledger_accounts:
            self.ledger_accounts[credit_account] = []
        
        self.ledger_accounts[credit_account].append({
            'date': date,
            'particulars': f"By {debit_account}",
            'debit': 0,
            'credit': amount,
            'narration': narration,
            'type': 'credit'
        })
    
    def get_ledger_report(self, account_name: str = None) -> pd.DataFrame:
        """Get ledger report for specific account or all accounts"""
        if account_name:
            return self._get_single_ledger(account_name)
        else:
            return self._get_all_ledgers()
    
    def _get_single_ledger(self, account_name: str) -> pd.DataFrame:
        """Get ledger for a single account"""
        if account_name not in self.ledger_accounts:
            return pd.DataFrame()
        
        entries = self.ledger_accounts[account_name]
        df = pd.DataFrame(entries)
        
        # Calculate running balance
        opening_balance = self.opening_balances.get(account_name, 0)
        df['balance'] = opening_balance
        
        for i, row in df.iterrows():
            balance_change = row['debit'] - row['credit']
            df.at[i, 'balance'] = opening_balance + balance_change
            opening_balance = df.at[i, 'balance']
        
        return df
    
    def _get_all_ledgers(self) -> pd.DataFrame:
        """Get consolidated ledger for all accounts"""
        all_ledgers = []
        
        for account_name, entries in self.ledger_accounts.items():
            account_df = self._get_single_ledger(account_name)
            account_df['account'] = account_name
            all_ledgers.append(account_df)
        
        if all_ledgers:
            return pd.concat(all_ledgers, ignore_index=True)
        else:
            return pd.DataFrame()
    
    def get_trial_balance(self) -> pd.DataFrame:
        """Generate trial balance from ledger accounts"""
        trial_balance = []
        
        for account_name in self.ledger_accounts.keys():
            ledger_df = self._get_single_ledger(account_name)
            
            if not ledger_df.empty:
                total_debit = ledger_df['debit'].sum()
                total_credit = ledger_df['credit'].sum()
                closing_balance = ledger_df['balance'].iloc[-1] if not ledger_df.empty else 0
                
                trial_balance.append({
                    'account': account_name,
                    'debit_total': total_debit,
                    'credit_total': total_credit,
                    'closing_balance': closing_balance,
                    'balance_type': 'Debit' if closing_balance > 0 else 'Credit'
                })
        
        return pd.DataFrame(trial_balance)
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse amount string to float"""
        try:
            clean_amount = amount_str.replace('₹', '').replace(',', '')
            return float(clean_amount)
        except:
            return 0.0
    
    def get_financial_summary(self) -> Dict[str, Any]:
        """Get financial summary from ledger"""
        trial_balance = self.get_trial_balance()
        
        if trial_balance.empty:
            return {}
        
        total_debits = trial_balance['debit_total'].sum()
        total_credits = trial_balance['credit_total'].sum()
        
        # Categorize accounts
        income_accounts = [acc for acc in trial_balance['account'] if 'income' in acc.lower()]
        expense_accounts = [acc for acc in trial_balance['account'] if 'expense' in acc.lower()]
        
        total_income = trial_balance[trial_balance['account'].isin(income_accounts)]['credit_total'].sum()
        total_expenses = trial_balance[trial_balance['account'].isin(expense_accounts)]['debit_total'].sum()
        net_profit = total_income - total_expenses
        
        return {
            'total_transactions': len(trial_balance),
            'total_debits': total_debits,
            'total_credits': total_credits,
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_profit': net_profit,
            'accounts_count': len(self.ledger_accounts),
            'trial_balance_balanced': abs(total_debits - total_credits) < 0.01
        }