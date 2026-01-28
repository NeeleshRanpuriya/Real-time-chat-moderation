"""
Database models for chat moderation system
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class ChatMessage(Base):
    """Store chat messages with moderation results"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, index=True)
    message = Column(Text, nullable=False)
    
    # Toxicity Detection
    toxicity_score = Column(Float, default=0.0)
    is_toxic = Column(Integer, default=0)  # 0=clean, 1=toxic
    toxic_categories = Column(JSON, default=dict)  # {"threat": 0.8, "insult": 0.6}
    
    # Intent Classification
    intent = Column(String(50), nullable=True)  # question, complaint, insult, etc.
    intent_confidence = Column(Float, default=0.0)
    
    # Tone Analysis
    tone = Column(String(50), nullable=True)  # polite, rude, aggressive, passive
    tone_confidence = Column(Float, default=0.0)
    
    # Coaching & Rewrite
    coaching_message = Column(Text, nullable=True)
    suggested_rewrite = Column(Text, nullable=True)
    
    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    room_id = Column(String(100), default="general", index=True)
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            "id": self.id,
            "username": self.username,
            "message": self.message,
            "toxicity_score": round(self.toxicity_score, 3),
            "is_toxic": bool(self.is_toxic),
            "toxic_categories": self.toxic_categories or {},
            "intent": self.intent,
            "intent_confidence": round(self.intent_confidence, 3) if self.intent_confidence else 0,
            "tone": self.tone,
            "tone_confidence": round(self.tone_confidence, 3) if self.tone_confidence else 0,
            "coaching_message": self.coaching_message,
            "suggested_rewrite": self.suggested_rewrite,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "room_id": self.room_id
        }


class ModerationStats(Base):
    """Store aggregated moderation statistics"""
    __tablename__ = "moderation_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    total_messages = Column(Integer, default=0)
    toxic_messages = Column(Integer, default=0)
    clean_messages = Column(Integer, default=0)
    
    # Intent breakdown
    questions = Column(Integer, default=0)
    complaints = Column(Integer, default=0)
    insults = Column(Integer, default=0)
    positive = Column(Integer, default=0)
    neutral = Column(Integer, default=0)
    
    # Tone breakdown
    polite = Column(Integer, default=0)
    rude = Column(Integer, default=0)
    aggressive = Column(Integer, default=0)
    
    date = Column(DateTime(timezone=True), server_default=func.now())
