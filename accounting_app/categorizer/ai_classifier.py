import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import json
from pathlib import Path
import joblib
import warnings
warnings.filterwarnings('ignore')

# Try to import sklearn components with proper error handling
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score
    SKLEARN_AVAILABLE = True
except ImportError as e:
    print(f"Scikit-learn not available: {e}")
    print("AI features will be disabled. Please install scikit-learn:")
    print("pip install scikit-learn")
    SKLEARN_AVAILABLE = False
    # Define fallback classes to avoid import errors
    class TfidfVectorizer:
        def __init__(self, *args, **kwargs):
            raise ImportError("Scikit-learn not installed")
    class RandomForestClassifier:
        def __init__(self, *args, **kwargs):
            raise ImportError("Scikit-learn not installed")

class AIClassifier:
    """
    AI-powered transaction classifier using machine learning
    Can be trained on historical data for better accuracy
    """
    
    def __init__(self, model_path: Optional[str] = None):
        if not SKLEARN_AVAILABLE:
            self.model = None
            self.vectorizer = None
            self.label_encoder = {}
            self.reverse_label_encoder = {}
            self.is_trained = False
            print("⚠️ AI Classifier disabled: scikit-learn not installed")
            return
        
        self.model = None
        self.vectorizer = TfidfVectorizer(max_features=1000, ngram_range=(1, 2))
        self.label_encoder = {}
        self.reverse_label_encoder = {}
        self.is_trained = False
        
        if model_path and Path(model_path).exists():
            self.load_model(model_path)
    
    def train(self, training_data: pd.DataFrame, text_column: str = 'description', 
              label_column: str = 'category', test_size: float = 0.2) -> Dict[str, Any]:
        """
        Train the AI classifier on labeled transaction data
        """
        if not SKLEARN_AVAILABLE:
            return {'error': 'Scikit-learn not installed. Please install scikit-learn to use AI features.'}
        
        try:
            # Prepare data
            X = training_data[text_column].fillna('').astype(str)
            y = training_data[label_column].fillna('miscellaneous').astype(str)
            
            # Encode labels
            self._fit_label_encoder(y)
            y_encoded = self._encode_labels(y)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y_encoded, test_size=test_size, random_state=42, stratify=y_encoded
            )
            
            # Vectorize text
            X_train_vec = self.vectorizer.fit_transform(X_train)
            X_test_vec = self.vectorizer.transform(X_test)
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=20,
                random_state=42,
                class_weight='balanced'
            )
            
            self.model.fit(X_train_vec, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_vec)
            accuracy = accuracy_score(y_test, y_pred)
            
            self.is_trained = True
            
            # Generate classification report
            y_test_decoded = self._decode_labels(y_test)
            y_pred_decoded = self._decode_labels(y_pred)
            report = classification_report(y_test_decoded, y_pred_decoded, output_dict=True)
            
            results = {
                'accuracy': accuracy,
                'model_type': 'RandomForest',
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'classes_trained': len(self.label_encoder),
                'classification_report': report
            }
            
            return results
            
        except Exception as e:
            print(f"Error training AI classifier: {e}")
            return {'error': str(e)}
    
    def predict(self, descriptions: List[str], return_confidence: bool = False) -> List[str]:
        """
        Predict categories for transaction descriptions
        """
        if not SKLEARN_AVAILABLE or not self.is_trained or self.model is None:
            # Fallback to rule-based if model not trained or sklearn not available
            return ['miscellaneous'] * len(descriptions)
        
        try:
            # Vectorize descriptions
            X_vec = self.vectorizer.transform(descriptions)
            
            # Predict
            predictions_encoded = self.model.predict(X_vec)
            predictions = self._decode_labels(predictions_encoded)
            
            if return_confidence:
                probabilities = self.model.predict_proba(X_vec)
                max_probabilities = np.max(probabilities, axis=1)
                return predictions, max_probabilities.tolist()
            
            return predictions
            
        except Exception as e:
            print(f"Error in AI prediction: {e}")
            return ['miscellaneous'] * len(descriptions)
    
    def predict_single(self, description: str, return_confidence: bool = False) -> str:
        """Predict category for a single transaction description"""
        predictions = self.predict([description], return_confidence)
        if return_confidence:
            return predictions[0][0], predictions[1][0]
        return predictions[0]
    
    def _fit_label_encoder(self, labels: pd.Series):
        """Fit label encoder to category labels"""
        unique_labels = labels.unique()
        self.label_encoder = {label: idx for idx, label in enumerate(unique_labels)}
        self.reverse_label_encoder = {idx: label for label, idx in self.label_encoder.items()}
    
    def _encode_labels(self, labels: pd.Series) -> np.ndarray:
        """Encode string labels to integers"""
        return labels.map(self.label_encoder).values
    
    def _decode_labels(self, encoded_labels: np.ndarray) -> List[str]:
        """Decode integer labels back to strings"""
        return [self.reverse_label_encoder.get(label, 'miscellaneous') for label in encoded_labels]
    
    def save_model(self, model_path: str):
        """Save trained model to file"""
        if not SKLEARN_AVAILABLE:
            print("Cannot save model: scikit-learn not installed")
            return
        
        try:
            model_data = {
                'model': self.model,
                'vectorizer': self.vectorizer,
                'label_encoder': self.label_encoder,
                'reverse_label_encoder': self.reverse_label_encoder,
                'is_trained': self.is_trained
            }
            joblib.dump(model_data, model_path)
            print(f"Model saved to {model_path}")
        except Exception as e:
            print(f"Error saving model: {e}")
    
    def load_model(self, model_path: str):
        """Load trained model from file"""
        if not SKLEARN_AVAILABLE:
            print("Cannot load model: scikit-learn not installed")
            return
        
        try:
            model_data = joblib.load(model_path)
            self.model = model_data['model']
            self.vectorizer = model_data['vectorizer']
            self.label_encoder = model_data['label_encoder']
            self.reverse_label_encoder = model_data['reverse_label_encoder']
            self.is_trained = model_data['is_trained']
            print(f"Model loaded from {model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
    
    def get_feature_importance(self, top_n: int = 20) -> pd.DataFrame:
        """Get feature importance from trained model"""
        if not SKLEARN_AVAILABLE or not self.is_trained or self.model is None:
            return pd.DataFrame()
        
        try:
            feature_names = self.vectorizer.get_feature_names_out()
            importances = self.model.feature_importances_
            
            # Create DataFrame with feature importance
            importance_df = pd.DataFrame({
                'feature': feature_names,
                'importance': importances
            }).sort_values('importance', ascending=False).head(top_n)
            
            return importance_df
            
        except Exception as e:
            print(f"Error getting feature importance: {e}")
            return pd.DataFrame()