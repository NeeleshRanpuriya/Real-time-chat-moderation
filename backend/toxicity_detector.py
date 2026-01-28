"""
Toxicity detection using HuggingFace transformers
"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class ToxicityDetector:
    """Detect toxic content using transformer models"""
    
    def __init__(self, model_name: str = "unitary/toxic-bert"):
        """
        Initialize toxicity detector
        
        Args:
            model_name: HuggingFace model name (default: unitary/toxic-bert)
        """
        logger.info(f"Loading toxicity model: {model_name}")
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"✅ Toxicity model loaded successfully on {self.device}")
        except Exception as e:
            logger.error(f"❌ Failed to load toxicity model: {e}")
            raise
    
    def predict(self, text: str, threshold: float = 0.5) -> Dict:
        """
        Predict toxicity for given text
        
        Args:
            text: Input text to analyze
            threshold: Toxicity threshold (0-1)
            
        Returns:
            Dictionary with toxicity score, categories, and is_toxic flag
        """
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)
            
            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.sigmoid(outputs.logits).cpu().numpy()[0]
            
            # Map predictions to categories
            # toxic-bert labels: toxic, severe_toxic, obscene, threat, insult, identity_hate
            categories = {
                "toxic": float(predictions[0]) if len(predictions) > 0 else 0.0,
                "severe_toxic": float(predictions[1]) if len(predictions) > 1 else 0.0,
                "obscene": float(predictions[2]) if len(predictions) > 2 else 0.0,
                "threat": float(predictions[3]) if len(predictions) > 3 else 0.0,
                "insult": float(predictions[4]) if len(predictions) > 4 else 0.0,
                "identity_hate": float(predictions[5]) if len(predictions) > 5 else 0.0,
            }
            
            # Calculate overall toxicity score (max of all categories)
            toxicity_score = float(np.max(predictions))
            
            # Determine if toxic
            is_toxic = toxicity_score >= threshold
            
            return {
                "toxicity_score": toxicity_score,
                "is_toxic": is_toxic,
                "categories": categories,
                "threshold": threshold
            }
            
        except Exception as e:
            logger.error(f"Error in toxicity prediction: {e}")
            return {
                "toxicity_score": 0.0,
                "is_toxic": False,
                "categories": {},
                "error": str(e)
            }
    
    def get_top_categories(self, categories: Dict[str, float], top_k: int = 3) -> list:
        """Get top K toxic categories"""
        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        return [cat for cat, score in sorted_cats[:top_k] if score > 0.3]
