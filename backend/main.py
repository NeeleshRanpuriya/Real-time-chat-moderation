"""
Main FastAPI application with WebSocket support
"""
import os
import logging
from datetime import datetime
from typing import List, Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import init_db, get_db
from models import ChatMessage, ModerationStats
from toxicity_detector import ToxicityDetector
from intent_classifier import IntentClassifier
from tone_analyzer import ToneAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Real-Time Chat Moderation API",
    description="AI-powered chat moderation with toxicity detection, intent classification, and communication coaching",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI models (loaded once at startup)
logger.info("🚀 Initializing AI models...")
toxicity_detector = None
intent_classifier = IntentClassifier()
tone_analyzer = ToneAnalyzer()

try:
    toxicity_detector = ToxicityDetector()
except Exception as e:
    logger.error(f"Failed to load toxicity detector: {e}")
    logger.warning("⚠️ Running without toxicity detection")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, username: str):
        await websocket.accept()
        self.active_connections.append(websocket)
        self.user_connections[username] = websocket
        logger.info(f"✅ User {username} connected. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket, username: str):
        self.active_connections.remove(websocket)
        if username in self.user_connections:
            del self.user_connections[username]
        logger.info(f"❌ User {username} disconnected. Total connections: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")

manager = ConnectionManager()


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    logger.info("🔧 Initializing database...")
    init_db()
    logger.info("✅ Application startup complete!")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Real-Time Chat Moderation API",
        "version": "1.0.0",
        "endpoints": {
            "websocket": "/ws/{username}",
            "messages": "/api/messages",
            "stats": "/api/stats"
        }
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "models": {
            "toxicity_detector": toxicity_detector is not None,
            "intent_classifier": True,
            "tone_analyzer": tone_analyzer.client is not None
        },
        "connections": len(manager.active_connections),
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/analyze")
async def analyze_message(
    message: str,
    username: str = "anonymous",
    db: Session = Depends(get_db)
):
    """
    Analyze a message without WebSocket (REST API)
    """
    result = await process_message(message, username, db)
    return result


async def process_message(message: str, username: str, db: Session) -> dict:
    """
    Core message processing logic:
    1. Toxicity detection
    2. Intent classification
    3. Tone analysis
    4. Coaching generation
    5. Rewrite suggestion
    """
    logger.info(f"Processing message from {username}: {message[:50]}...")
    
    # 1. Toxicity Detection
    toxicity_result = {"toxicity_score": 0.0, "is_toxic": False, "categories": {}}
    if toxicity_detector:
        try:
            toxicity_result = toxicity_detector.predict(message)
        except Exception as e:
            logger.error(f"Toxicity detection failed: {e}")
    
    # 2. Intent Classification
    intent, intent_confidence = intent_classifier.classify(message)
    
    # 3. Tone Analysis
    tone_result = tone_analyzer.analyze_tone(
        message,
        toxicity_result["toxicity_score"],
        intent
    )
    
    # 4. Generate Coaching
    coaching_message = None
    suggested_rewrite = None
    
    if toxicity_result["toxicity_score"] > 0.3 or tone_result["tone"] in ["rude", "aggressive"]:
        coaching_message = tone_analyzer.generate_coaching(
            message,
            tone_result["tone"],
            toxicity_result["toxicity_score"],
            intent
        )
        
        suggested_rewrite = tone_analyzer.suggest_rewrite(
            message,
            tone_result["tone"],
            toxicity_result["toxicity_score"]
        )
    
    # 5. Save to database
    chat_message = ChatMessage(
        username=username,
        message=message,
        toxicity_score=toxicity_result["toxicity_score"],
        is_toxic=int(toxicity_result["is_toxic"]),
        toxic_categories=toxicity_result.get("categories", {}),
        intent=intent,
        intent_confidence=intent_confidence,
        tone=tone_result["tone"],
        tone_confidence=tone_result["confidence"],
        coaching_message=coaching_message,
        suggested_rewrite=suggested_rewrite,
        room_id="general"
    )
    
    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)
    
    # 6. Prepare response
    response = {
        "id": chat_message.id,
        "username": username,
        "message": message,
        "analysis": {
            "toxicity": {
                "score": round(toxicity_result["toxicity_score"], 3),
                "is_toxic": toxicity_result["is_toxic"],
                "categories": toxicity_result.get("categories", {}),
                "top_categories": toxicity_detector.get_top_categories(
                    toxicity_result.get("categories", {})
                ) if toxicity_detector else []
            },
            "intent": {
                "type": intent,
                "confidence": round(intent_confidence, 3),
                "explanation": intent_classifier.get_intent_explanation(intent)
            },
            "tone": {
                "type": tone_result["tone"],
                "confidence": round(tone_result["confidence"], 3),
                "explanation": tone_result.get("explanation", "")
            }
        },
        "coaching": {
            "message": coaching_message,
            "suggested_rewrite": suggested_rewrite
        },
        "timestamp": chat_message.timestamp.isoformat()
    }
    
    logger.info(f"✅ Message processed: toxicity={toxicity_result['toxicity_score']:.2f}, intent={intent}, tone={tone_result['tone']}")
    
    return response


@app.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for real-time chat
    """
    await manager.connect(websocket, username)
    
    # Send welcome message
    await websocket.send_json({
        "type": "system",
        "message": f"Welcome {username}! You are now connected to the moderated chat.",
        "timestamp": datetime.now().isoformat()
    })
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_text = data.get("message", "").strip()
            
            if not message_text:
                continue
            
            # Process message
            result = await process_message(message_text, username, db)
            
            # Send analysis back to sender
            await websocket.send_json({
                "type": "analysis",
                **result
            })
            
            # Broadcast message to all users (with moderation info)
            await manager.broadcast({
                "type": "message",
                "username": username,
                "message": message_text,
                "is_toxic": result["analysis"]["toxicity"]["is_toxic"],
                "toxicity_score": result["analysis"]["toxicity"]["score"],
                "timestamp": result["timestamp"]
            })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, username)
        await manager.broadcast({
            "type": "system",
            "message": f"{username} left the chat",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"WebSocket error for {username}: {e}")
        manager.disconnect(websocket, username)


@app.get("/api/messages")
async def get_messages(
    limit: int = 50,
    room_id: str = "general",
    db: Session = Depends(get_db)
):
    """Get recent chat messages"""
    messages = db.query(ChatMessage)\
        .filter(ChatMessage.room_id == room_id)\
        .order_by(ChatMessage.timestamp.desc())\
        .limit(limit)\
        .all()
    
    return {
        "messages": [msg.to_dict() for msg in reversed(messages)],
        "count": len(messages)
    }


@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Get moderation statistics"""
    total = db.query(ChatMessage).count()
    toxic = db.query(ChatMessage).filter(ChatMessage.is_toxic == 1).count()
    
    # Intent breakdown
    intents = db.query(ChatMessage.intent, db.func.count(ChatMessage.id))\
        .group_by(ChatMessage.intent)\
        .all()
    
    # Tone breakdown
    tones = db.query(ChatMessage.tone, db.func.count(ChatMessage.id))\
        .group_by(ChatMessage.tone)\
        .all()
    
    return {
        "total_messages": total,
        "toxic_messages": toxic,
        "clean_messages": total - toxic,
        "toxicity_rate": round(toxic / total * 100, 2) if total > 0 else 0,
        "intents": {intent: count for intent, count in intents if intent},
        "tones": {tone: count for tone, count in tones if tone},
        "active_connections": len(manager.active_connections)
    }


@app.delete("/api/messages/{message_id}")
async def delete_message(message_id: int, db: Session = Depends(get_db)):
    """Delete a message (moderation action)"""
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    db.delete(message)
    db.commit()
    
    return {"message": "Message deleted successfully", "id": message_id}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
