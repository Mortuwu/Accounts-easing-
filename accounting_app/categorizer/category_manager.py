import pandas as pd
import re
from typing import Dict, List, Any, Optional
from .rule_engine import RuleEngine
from .ai_classifier import AIClassifier

class CategoryManager:
    """
    Main category manager that combines rule-based and AI categorization
    Provides a unified interface for transaction categorization
    """
    
    def __init__(self, categories_file: str = 'config/categories.json', 
                 ai_model_path: Optional[str] = None):
        self.rule_engine = RuleEngine(categories_file)
        self.ai_classifier = AIClassifier(ai_model_path)
        self.use_ai = False
        
        # Categorization history for learning
        self.categorization_history = []
    
    def set_ai_mode(self, enabled: bool):
        """Enable or disable AI categorization"""
        self.use_ai = enabled
    
    def categorize_transaction(self, description: str, amount: float, 
                             transaction_type: str) -> Dict[str, Any]:
        """
        Categorize a transaction using combined approach
        
        Returns:
            Dictionary with category and metadata
        """
        # Rule-based categorization
        rule_category = self.rule_engine.categorize_transaction(
            description, amount, transaction_type, use_ai=False
        )
        
        result = {
            'category': rule_category,
            'method': 'rule_based',
            'confidence': self.rule_engine._calculate_confidence(description, rule_category),
            'description': description,
            'amount': amount,
            'type': transaction_type
        }
        
        # AI categorization if enabled and trained
        if self.use_ai and self.ai_classifier.is_trained:
            ai_category, ai_confidence = self.ai_classifier.predict_single(
                description, return_confidence=True
            )
            
            # Use AI category if confidence is high
            if ai_confidence > 0.7:  # Threshold for trusting AI
                result.update({
                    'category': ai_category,
                    'method': 'ai',
                    'confidence': ai_confidence,
                    'ai_confidence': ai_confidence
                })
        
        # Store in history
        self.categorization_history.append(result.copy())
        
        return result
    
    def categorize_dataframe(self, transactions_df: pd.DataFrame) -> pd.DataFrame:
        """Categorize all transactions in a DataFrame"""
        categorized_data = []
        
        for _, transaction in transactions_df.iterrows():
            result = self.categorize_transaction(
                transaction['description'],
                transaction['amount'],
                transaction['type']
            )
            categorized_data.append(result)
        
        # Convert to DataFrame and merge with original
        result_df = pd.DataFrame(categorized_data)
        
        # Keep original columns and add categorization results
        final_df = transactions_df.copy()
        final_df['category'] = result_df['category']
        final_df['categorization_method'] = result_df['method']
        final_df['confidence_score'] = result_df['confidence']
        
        return final_df
    
    def train_ai_model(self, training_data: pd.DataFrame, 
                      text_column: str = 'description',
                      label_column: str = 'category') -> Dict[str, Any]:
        """Train the AI model on labeled data"""
        results = self.ai_classifier.train(training_data, text_column, label_column)
        
        if 'error' not in results:
            self.use_ai = True  # Enable AI after successful training
        
        return results
    
    def get_category_analysis(self, transactions_df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive analysis of categorization results"""
        if 'category' not in transactions_df.columns:
            return {}
        
        stats = self.rule_engine.get_categorization_stats(transactions_df)
        
        # Add method distribution if available
        if 'categorization_method' in transactions_df.columns:
            method_counts = transactions_df['categorization_method'].value_counts().to_dict()
            stats['method_distribution'] = method_counts
        
        # Category distribution by transaction type
        credit_categories = transactions_df[transactions_df['type'] == 'CR']['category'].value_counts().to_dict()
        debit_categories = transactions_df[transactions_df['type'] == 'DR']['category'].value_counts().to_dict()
        
        stats['credit_categories'] = credit_categories
        stats['debit_categories'] = debit_categories
        
        return stats
    
    def export_training_data(self, output_path: str):
        """Export categorization history as training data"""
        if not self.categorization_history:
            return
        
        df = pd.DataFrame(self.categorization_history)
        df.to_csv(output_path, index=False)
        print(f"Training data exported to {output_path}")
    
    def get_suggested_categories(self, description: str, top_n: int = 3) -> List[Dict[str, Any]]:
        """Get suggested categories for a description with confidence scores"""
        suggestions = []
        
        # Rule-based suggestions
        desc_lower = description.lower()
        for category_name, category_data in self.rule_engine.categories.items():
            keywords = category_data.get('keywords', [])
            for keyword in keywords:
                if keyword in desc_lower:
                    confidence = 0.9 if re.search(r'\b' + re.escape(keyword) + r'\b', desc_lower) else 0.7
                    suggestions.append({
                        'category': category_name,
                        'confidence': confidence,
                        'method': 'keyword',
                        'matched_keyword': keyword
                    })
                    break  # One suggestion per category
        
        # AI suggestions if available
        if self.use_ai and self.ai_classifier.is_trained:
            try:
                ai_predictions, ai_confidences = self.ai_classifier.predict([description], return_confidence=True)
                suggestions.append({
                    'category': ai_predictions[0],
                    'confidence': ai_confidences[0],
                    'method': 'ai',
                    'matched_keyword': None
                })
            except:
                pass
        
        # Sort by confidence and return top N
        suggestions.sort(key=lambda x: x['confidence'], reverse=True)
        return suggestions[:top_n]
    
    def add_feedback(self, transaction_data: Dict[str, Any], correct_category: str):
        """Add feedback to improve categorization"""
        feedback_entry = {
            'description': transaction_data.get('description', ''),
            'amount': transaction_data.get('amount', 0),
            'type': transaction_data.get('type', 'DR'),
            'original_category': transaction_data.get('category', ''),
            'correct_category': correct_category,
            'timestamp': pd.Timestamp.now()
        }
        
        self.categorization_history.append(feedback_entry)
        
        # TODO: Implement online learning to update models based on feedback
        print(f"Feedback received: {correct_category} for '{transaction_data.get('description', '')}'")