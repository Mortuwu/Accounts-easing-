import json
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class RuleEngine:
    def __init__(self, categories_file='config/categories.json'):
        self.categories = self._load_categories(categories_file)
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=1000)
        self._build_keyword_matrix()
        
        # Transaction type patterns
        self.type_patterns = {
            'credit': ['cr', 'credit', 'deposit', 'received', 'refund'],
            'debit': ['dr', 'debit', 'withdrawal', 'payment', 'paid']
        }
    
    def _load_categories(self, categories_file: str) -> Dict[str, Any]:
        """Load categories from JSON file with validation"""
        try:
            file_path = Path(categories_file)
            if not file_path.exists():
                # Fallback to default categories
                return self._get_default_categories()
            
            with open(file_path, 'r', encoding='utf-8') as f:
                categories = json.load(f)
            
            # Validate categories structure
            validated_categories = {}
            for category_name, category_data in categories.items():
                if isinstance(category_data, dict):
                    validated_categories[category_name] = {
                        'keywords': category_data.get('keywords', []),
                        'account_name': category_data.get('account_name', category_name.title()),
                        'type': category_data.get('type', 'expense'),
                        'priority': category_data.get('priority', 1),
                        'patterns': category_data.get('patterns', [])
                    }
            
            return validated_categories
            
        except Exception as e:
            print(f"Error loading categories: {e}")
            return self._get_default_categories()
    
    def _get_default_categories(self) -> Dict[str, Any]:
        """Get default categories if config file is missing"""
        return {
            "donation_income": {
                "keywords": ["donation", "donated", "contribution", "charity", "grant", "gift"],
                "account_name": "Donation Income",
                "type": "income",
                "priority": 1,
                "patterns": [r"donation", r"contribution", r"charity"]
            },
            "salary_income": {
                "keywords": ["salary", "payroll", "wages", "stipend", "compensation"],
                "account_name": "Salary Income", 
                "type": "income",
                "priority": 1
            },
            "food_expense": {
                "keywords": ["restaurant", "cafe", "food", "snacks", "samosa", "meal", "lunch", "dinner"],
                "account_name": "Food Expense",
                "type": "expense",
                "priority": 2
            },
            "transport_expense": {
                "keywords": ["fuel", "petrol", "diesel", "bus", "train", "metro", "taxi", "uber", "ola"],
                "account_name": "Transport Expense",
                "type": "expense",
                "priority": 2
            },
            "cash_withdrawal": {
                "keywords": ["atm", "cash", "withdrawal", "wdl", "cash withdraw"],
                "account_name": "Cash Account",
                "type": "transfer",
                "priority": 1
            },
            "bank_transfer": {
                "keywords": ["neft", "imps", "rtgs", "upi", "transfer"],
                "account_name": "Bank Transfer",
                "type": "transfer",
                "priority": 1
            },
            "miscellaneous": {
                "keywords": [],
                "account_name": "Miscellaneous",
                "type": "expense",
                "priority": 99
            }
        }
    
    def _build_keyword_matrix(self):
        """Build TF-IDF matrix for keyword matching"""
        try:
            # Create corpus from all keywords
            corpus = []
            self.category_list = []
            
            for category_name, category_data in self.categories.items():
                keywords = category_data.get('keywords', [])
                if keywords:
                    # Add each keyword as a separate document
                    for keyword in keywords:
                        corpus.append(keyword)
                        self.category_list.append(category_name)
            
            if corpus:
                self.keyword_matrix = self.vectorizer.fit_transform(corpus)
            else:
                self.keyword_matrix = None
                
        except Exception as e:
            print(f"Error building keyword matrix: {e}")
            self.keyword_matrix = None
    
    def categorize_transaction(self, description: str, amount: float, transaction_type: str, 
                             use_ai: bool = False) -> str:
        """
        Categorize transaction using rule-based approach with optional AI enhancement
        
        Args:
            description: Transaction description
            amount: Transaction amount
            transaction_type: CR or DR
            use_ai: Whether to use AI-enhanced categorization
            
        Returns:
            Category name
        """
        description_lower = description.lower()
        
        # Method 1: Exact keyword matching (highest priority)
        exact_match = self._exact_keyword_match(description_lower)
        if exact_match:
            return exact_match
        
        # Method 2: Pattern matching with regex
        pattern_match = self._pattern_match(description_lower)
        if pattern_match:
            return pattern_match
        
        # Method 3: TF-IDF similarity matching
        if use_ai and self.keyword_matrix is not None:
            similarity_match = self._similarity_match(description_lower)
            if similarity_match:
                return similarity_match
        
        # Method 4: Amount-based heuristics
        amount_match = self._amount_based_heuristics(description_lower, amount, transaction_type)
        if amount_match:
            return amount_match
        
        # Method 5: Default based on transaction type
        return self._get_default_category(transaction_type)
    
    def _exact_keyword_match(self, description: str) -> Optional[str]:
        """Match using exact keywords with priority handling"""
        matched_categories = []
        
        for category_name, category_data in self.categories.items():
            keywords = category_data.get('keywords', [])
            priority = category_data.get('priority', 1)
            
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', description):
                    matched_categories.append((category_name, priority))
                    break  # One match per category is enough
        
        if matched_categories:
            # Return highest priority match
            matched_categories.sort(key=lambda x: x[1])
            return matched_categories[0][0]
        
        return None
    
    def _pattern_match(self, description: str) -> Optional[str]:
        """Match using regex patterns"""
        for category_name, category_data in self.categories.items():
            patterns = category_data.get('patterns', [])
            for pattern in patterns:
                if re.search(pattern, description, re.IGNORECASE):
                    return category_name
        return None
    
    def _similarity_match(self, description: str, threshold: float = 0.3) -> Optional[str]:
        """Match using TF-IDF cosine similarity"""
        try:
            if self.keyword_matrix is None:
                return None
            
            # Transform description to TF-IDF
            desc_vector = self.vectorizer.transform([description])
            
            # Calculate cosine similarity with all keywords
            similarities = cosine_similarity(desc_vector, self.keyword_matrix)
            
            # Find best match
            max_similarity_idx = np.argmax(similarities)
            max_similarity = similarities[0, max_similarity_idx]
            
            if max_similarity > threshold:
                return self.category_list[max_similarity_idx]
            
            return None
            
        except Exception as e:
            print(f"Error in similarity matching: {e}")
            return None
    
    def _amount_based_heuristics(self, description: str, amount: float, transaction_type: str) -> Optional[str]:
        """Use amount-based heuristics for categorization"""
        # Round amounts for common transaction types
        rounded_amount = round(amount)
        
        # Common ATM withdrawal amounts
        atm_amounts = [500, 1000, 2000, 5000, 10000, 20000]
        if 'atm' in description and rounded_amount in atm_amounts:
            return 'cash_withdrawal'
        
        # Common food expense patterns
        if transaction_type == 'DR' and amount < 1000:
            food_indicators = ['cafe', 'restaurant', 'food', 'meal', 'snack']
            if any(indicator in description for indicator in food_indicators):
                return 'food_expense'
        
        # Common transport amounts
        if transaction_type == 'DR' and amount <= 500:
            transport_indicators = ['fuel', 'petrol', 'bus', 'taxi', 'uber']
            if any(indicator in description for indicator in transport_indicators):
                return 'transport_expense'
        
        return None
    
    def _get_default_category(self, transaction_type: str) -> str:
        """Get default category based on transaction type"""
        if transaction_type == 'CR':
            return 'donation_income'  # Default for credits
        else:
            return 'miscellaneous'    # Default for debits
    
    def get_category_details(self, category_name: str) -> Dict[str, Any]:
        """Get detailed information about a category"""
        return self.categories.get(category_name, {})
    
    def get_account_name(self, category: str) -> str:
        """Get accounting account name for category"""
        return self.categories.get(category, {}).get('account_name', 'Miscellaneous Account')
    
    def get_category_type(self, category: str) -> str:
        """Get category type (income, expense, transfer, asset, liability)"""
        return self.categories.get(category, {}).get('type', 'expense')
    
    def add_custom_category(self, category_name: str, keywords: List[str], 
                          account_name: str, category_type: str = 'expense', priority: int = 1):
        """Add custom category to the engine"""
        self.categories[category_name] = {
            'keywords': keywords,
            'account_name': account_name,
            'type': category_type,
            'priority': priority
        }
        # Rebuild keyword matrix
        self._build_keyword_matrix()
    
    def categorize_dataframe(self, transactions_df: pd.DataFrame, use_ai: bool = False) -> pd.DataFrame:
        """Categorize all transactions in a DataFrame"""
        categorized_df = transactions_df.copy()
        
        categories = []
        confidence_scores = []
        
        for _, transaction in categorized_df.iterrows():
            category = self.categorize_transaction(
                transaction['description'],
                transaction['amount'],
                transaction['type'],
                use_ai
            )
            categories.append(category)
            
            # Calculate confidence score (simple version)
            confidence = self._calculate_confidence(transaction['description'], category)
            confidence_scores.append(confidence)
        
        categorized_df['category'] = categories
        categorized_df['confidence_score'] = confidence_scores
        
        return categorized_df
    
    def _calculate_confidence(self, description: str, category: str) -> float:
        """Calculate confidence score for categorization"""
        description_lower = description.lower()
        category_data = self.categories.get(category, {})
        keywords = category_data.get('keywords', [])
        
        # Check for exact keyword matches
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', description_lower):
                return 0.9  # High confidence for exact matches
        
        # Check for partial matches
        for keyword in keywords:
            if keyword in description_lower:
                return 0.7  # Medium confidence for partial matches
        
        # Low confidence for default categories
        if category in ['miscellaneous', 'donation_income']:
            return 0.3
        
        return 0.5  # Default confidence
    
    def get_categorization_stats(self, transactions_df: pd.DataFrame) -> Dict[str, Any]:
        """Get statistics about categorization results"""
        if 'category' not in transactions_df.columns:
            return {}
        
        category_counts = transactions_df['category'].value_counts().to_dict()
        total_transactions = len(transactions_df)
        
        stats = {
            'total_transactions': total_transactions,
            'category_distribution': category_counts,
            'unique_categories': len(category_counts),
            'most_common_category': transactions_df['category'].mode().iloc[0] if not transactions_df.empty else None
        }
        
        if 'confidence_score' in transactions_df.columns:
            stats['average_confidence'] = transactions_df['confidence_score'].mean()
            stats['low_confidence_count'] = len(transactions_df[transactions_df['confidence_score'] < 0.5])
        
        return stats