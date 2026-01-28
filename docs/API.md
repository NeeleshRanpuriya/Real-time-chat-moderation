# API Documentation

## Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## REST API Endpoints

### Health Check

#### GET /
Check if API is online

**Response**:
```json
{
  "status": "online",
  "service": "Real-Time Chat Moderation API",
  "version": "1.0.0",
  "endpoints": {
    "websocket": "/ws/{username}",
    "messages": "/api/messages",
    "stats": "/api/stats"
  }
}
```

#### GET /api/health
Detailed health check with model status

**Response**:
```json
{
  "status": "healthy",
  "models": {
    "toxicity_detector": true,
    "intent_classifier": true,
    "tone_analyzer": true
  },
  "connections": 3,
  "timestamp": "2024-01-28T10:30:00Z"
}
```

### Message Analysis

#### POST /api/analyze
Analyze a message without WebSocket connection

**Request Body**:
```json
{
  "message": "You're an idiot",
  "username": "john_doe"
}
```

**Query Parameters**:
- `message` (required): The message text to analyze
- `username` (optional): Username, default "anonymous"

**Response**:
```json
{
  "id": 123,
  "username": "john_doe",
  "message": "You're an idiot",
  "analysis": {
    "toxicity": {
      "score": 0.856,
      "is_toxic": true,
      "categories": {
        "toxic": 0.856,
        "insult": 0.923,
        "threat": 0.112,
        "obscene": 0.045
      },
      "top_categories": ["insult", "toxic"]
    },
    "intent": {
      "type": "insult",
      "confidence": 0.98,
      "explanation": "User is using insulting or disrespectful language"
    },
    "tone": {
      "type": "rude",
      "confidence": 0.92,
      "explanation": "Message contains disrespectful language"
    }
  },
  "coaching": {
    "message": "Your message comes across as disrespectful. Consider using more neutral language...",
    "suggested_rewrite": "I respectfully disagree with your approach"
  },
  "timestamp": "2024-01-28T10:30:00Z"
}
```

### Message History

#### GET /api/messages
Retrieve chat message history

**Query Parameters**:
- `limit` (optional): Maximum messages to return (default: 50)
- `room_id` (optional): Chat room identifier (default: "general")

**Example Request**:
```
GET /api/messages?limit=20&room_id=general
```

**Response**:
```json
{
  "messages": [
    {
      "id": 1,
      "username": "alice",
      "message": "Hello everyone!",
      "toxicity_score": 0.012,
      "is_toxic": false,
      "toxic_categories": {},
      "intent": "positive",
      "intent_confidence": 0.85,
      "tone": "polite",
      "tone_confidence": 0.89,
      "coaching_message": null,
      "suggested_rewrite": null,
      "timestamp": "2024-01-28T10:25:00Z",
      "room_id": "general"
    },
    // ... more messages
  ],
  "count": 20
}
```

### Statistics

#### GET /api/stats
Get moderation statistics

**Response**:
```json
{
  "total_messages": 150,
  "toxic_messages": 23,
  "clean_messages": 127,
  "toxicity_rate": 15.33,
  "intents": {
    "question": 35,
    "positive": 42,
    "complaint": 18,
    "insult": 15,
    "neutral": 25,
    "disagreement": 10,
    "threat": 5
  },
  "tones": {
    "polite": 80,
    "neutral": 35,
    "rude": 20,
    "aggressive": 10,
    "passive-aggressive": 5
  },
  "active_connections": 5
}
```

### Moderation Actions

#### DELETE /api/messages/{message_id}
Delete a message (moderation action)

**Path Parameters**:
- `message_id` (required): ID of the message to delete

**Example Request**:
```
DELETE /api/messages/123
```

**Response**:
```json
{
  "message": "Message deleted successfully",
  "id": 123
}
```

**Error Response** (404):
```json
{
  "detail": "Message not found"
}
```

## WebSocket API

### Connection

#### WS /ws/{username}
Establish WebSocket connection for real-time chat

**Path Parameters**:
- `username` (required): Unique username for the session

**Example Connection**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/john_doe')
```

### Message Types

#### 1. System Messages
Server → Client notifications

```json
{
  "type": "system",
  "message": "Welcome john_doe! You are now connected to the moderated chat.",
  "timestamp": "2024-01-28T10:30:00Z"
}
```

#### 2. Chat Messages
Broadcast to all connected clients

```json
{
  "type": "message",
  "username": "alice",
  "message": "Hello everyone!",
  "is_toxic": false,
  "toxicity_score": 0.012,
  "timestamp": "2024-01-28T10:30:00Z"
}
```

#### 3. Analysis Messages
Personal analysis sent only to message sender

```json
{
  "type": "analysis",
  "id": 123,
  "username": "john_doe",
  "message": "You're an idiot",
  "analysis": {
    "toxicity": {
      "score": 0.856,
      "is_toxic": true,
      "categories": {...},
      "top_categories": ["insult", "toxic"]
    },
    "intent": {
      "type": "insult",
      "confidence": 0.98,
      "explanation": "..."
    },
    "tone": {
      "type": "rude",
      "confidence": 0.92,
      "explanation": "..."
    }
  },
  "coaching": {
    "message": "...",
    "suggested_rewrite": "..."
  },
  "timestamp": "2024-01-28T10:30:00Z"
}
```

### Sending Messages

Client → Server message format:

```json
{
  "message": "Hello, how are you?"
}
```

### Connection Lifecycle

1. **Connect**: Client connects to `/ws/{username}`
2. **Welcome**: Server sends system welcome message
3. **Chat**: Client sends/receives messages
4. **Analysis**: Server sends personal analysis for each message
5. **Broadcast**: Server broadcasts messages to all clients
6. **Disconnect**: Client closes connection, server notifies others

### Example Client Implementation (JavaScript)

```javascript
// Connect
const ws = new WebSocket('ws://localhost:8000/ws/john_doe')

// Handle connection open
ws.onopen = () => {
  console.log('Connected!')
}

// Send message
function sendMessage(text) {
  ws.send(JSON.stringify({ message: text }))
}

// Receive messages
ws.onmessage = (event) => {
  const data = JSON.parse(event.data)
  
  if (data.type === 'system') {
    console.log('System:', data.message)
  } else if (data.type === 'message') {
    console.log(`${data.username}: ${data.message}`)
  } else if (data.type === 'analysis') {
    console.log('Analysis:', data.analysis)
  }
}

// Handle disconnection
ws.onclose = () => {
  console.log('Disconnected')
}

// Handle errors
ws.onerror = (error) => {
  console.error('WebSocket error:', error)
}
```

## Error Codes

### HTTP Status Codes

- `200 OK`: Request successful
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Invalid request parameters
- `500 Internal Server Error`: Server error

### WebSocket Close Codes

- `1000`: Normal closure
- `1001`: Going away (client navigating away)
- `1006`: Abnormal closure (connection lost)

## Rate Limiting

Currently no rate limiting is implemented. For production:
- Consider implementing rate limiting per user
- Limit WebSocket connections per IP
- Throttle message sending

## Authentication

Currently no authentication is implemented. For production:
- Implement JWT tokens
- Add user registration/login
- Secure WebSocket connections with tokens

## CORS Configuration

Development mode allows all origins. For production:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Data Models

### ChatMessage Model

```python
class ChatMessage:
    id: int                           # Primary key
    username: str                     # User identifier
    message: str                      # Message text
    toxicity_score: float            # 0.0-1.0
    is_toxic: int                    # 0 or 1
    toxic_categories: dict           # JSON object
    intent: str                      # Intent type
    intent_confidence: float         # 0.0-1.0
    tone: str                        # Tone type
    tone_confidence: float           # 0.0-1.0
    coaching_message: str            # Coaching text
    suggested_rewrite: str           # Polite alternative
    timestamp: datetime              # Creation time
    room_id: str                     # Chat room ID
```

## Testing the API

### Using curl

```bash
# Health check
curl http://localhost:8000/

# Analyze message
curl -X POST http://localhost:8000/api/analyze \
  -d "message=You're an idiot" \
  -d "username=test_user"

# Get messages
curl http://localhost:8000/api/messages?limit=10

# Get stats
curl http://localhost:8000/api/stats
```

### Using Python

```python
import requests

# Analyze message
response = requests.post(
    'http://localhost:8000/api/analyze',
    params={
        'message': "You're an idiot",
        'username': 'test_user'
    }
)
print(response.json())
```

### Using WebSocket (Python)

```python
import asyncio
import websockets
import json

async def chat():
    uri = "ws://localhost:8000/ws/test_user"
    async with websockets.connect(uri) as websocket:
        # Send message
        await websocket.send(json.dumps({
            "message": "Hello from Python!"
        }))
        
        # Receive responses
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data}")

asyncio.run(chat())
```

## Best Practices

1. **Connection Management**
   - Implement reconnection logic in clients
   - Handle connection drops gracefully
   - Close connections properly

2. **Error Handling**
   - Always check response status codes
   - Implement fallback for model failures
   - Log errors for debugging

3. **Performance**
   - Batch requests when possible
   - Cache frequent queries
   - Use WebSocket for real-time needs

4. **Security**
   - Sanitize user inputs
   - Implement rate limiting
   - Use HTTPS in production
   - Add authentication for sensitive operations
