"""
Intent classification module
"""
import re
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class IntentClassifier:
    """Classify user intent from messages"""
    
    def __init__(self):
        """Initialize intent classifier with keyword patterns"""
        self.intent_patterns = {
            "question": [
                r"\?$",  # Ends with question mark
                r"^(what|when|where|who|why|how|which|can|could|would|should|is|are|do|does)",
                r"(help|explain|clarify|tell me|show me)",
            ],
            "complaint": [
                r"(don't|dont|never|always|terrible|awful|worst|hate|sick of)",
                r"(problem|issue|bug|error|broken|not working|doesn't work)",
                r"(disappointed|frustrated|angry|annoyed)",
            ],
            "insult": [
                r"(stupid|idiot|dumb|fool|moron|loser|pathetic)",
                r"(shut up|get lost|screw you)",
                r"(nobody cares|no one asked|nobody asked)",
            ],
            "threat": [
                r"(i'll|ill|gonna|going to).*(kill|hurt|destroy|ruin|attack)",
                r"(watch out|you'll regret|you're dead|you're done)",
            ],
            "positive": [
                r"(thank|thanks|appreciate|grateful|awesome|great|excellent|amazing|love)",
                r"(good job|well done|nice|perfect|fantastic|wonderful)",
                r"(😊|😄|😁|👍|❤️|💯)",
            ],
            "disagreement": [
                r"(i disagree|don't agree|wrong|incorrect|that's not)",
                r"(actually|in fact|to be honest|honestly)",
                r"(but|however|although)",
            ],
            "neutral": [],  # Default fallback
        }
    
    def classify(self, text: str) -> Tuple[str, float]:
        """
        Classify intent of the message
        
        Args:
            text: Input message
            
        Returns:
            Tuple of (intent, confidence_score)
        """
        text_lower = text.lower().strip()
        
        # Check each intent pattern
        intent_scores = {}
        
        for intent, patterns in self.intent_patterns.items():
            if intent == "neutral":
                continue
                
            score = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    score += 1
            
            if score > 0:
                # Normalize by number of patterns
                intent_scores[intent] = score / len(patterns)
        
        # Get highest scoring intent
        if intent_scores:
            intent = max(intent_scores, key=intent_scores.get)
            confidence = min(intent_scores[intent], 1.0)
            return intent, confidence
        
        # Default to neutral
        return "neutral", 0.5
    
    def get_intent_explanation(self, intent: str) -> str:
        """Get human-readable explanation for intent"""
        explanations = {
            "question": "User is asking a question or seeking information",
            "complaint": "User is expressing dissatisfaction or reporting an issue",
            "insult": "User is using insulting or disrespectful language",
            "threat": "User is making threatening statements",
            "positive": "User is expressing positive sentiment or gratitude",
            "disagreement": "User is disagreeing or challenging a statement",
            "neutral": "User is making a neutral statement or observation",
        }
        return explanations.get(intent, "Unknown intent")
