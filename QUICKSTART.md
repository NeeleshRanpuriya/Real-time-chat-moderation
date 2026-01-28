# 🚀 Quick Start Guide

## For College Project Demo

This guide will get you up and running in under 10 minutes!

## Prerequisites

- Python 3.8+ installed
- Node.js 18+ installed
- Terminal/Command Prompt access

## Step 1: Clone or Download

If you have the project folder, navigate to it:
```bash
cd /path/to/webapp
```

## Step 2: Backend Setup (5 minutes)

### Option A: Automatic Setup (Recommended)

```bash
cd backend
./setup.sh
```

### Option B: Manual Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (this takes 3-4 minutes)
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Initialize database
python -c "from database import init_db; init_db()"
```

### Configure OpenAI (Optional)

Edit `backend/.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-key-here
```

**Note**: The system works WITHOUT OpenAI, but tone analysis will use fallback rules.

### Start Backend Server

```bash
# Make sure you're in backend/ and venv is activated
python main.py
```

✅ Backend running at: **http://localhost:8000**

## Step 3: Frontend Setup (2 minutes)

**Open a new terminal window** (keep backend running!)

### Option A: Automatic Setup

```bash
cd frontend
./setup.sh
```

### Option B: Manual Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

✅ Frontend running at: **http://localhost:3000**

## Step 4: Test the System

1. **Open browser**: Go to http://localhost:3000

2. **Enter username**: Type any username (e.g., "Alice")

3. **Click "Connect to Chat"**

4. **Send test messages**:
   - Clean: "Hello everyone, how are you?"
   - Question: "What time is the meeting?"
   - Toxic: "You're an idiot" (for testing detection)

5. **Watch the magic** ✨:
   - Toxicity score appears instantly
   - Intent is classified
   - Tone is analyzed
   - Coaching suggestions appear
   - Polite rewrites are offered

## Step 5: Test Multi-User Chat

1. Open **another browser window** (or incognito)
2. Go to http://localhost:3000
3. Enter a **different username** (e.g., "Bob")
4. Connect and chat between windows!

## Common Issues

### Backend won't start

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Fix**: Make sure virtual environment is activated:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend won't start

**Error**: `command not found: npm`

**Fix**: Install Node.js from https://nodejs.org

### Model downloading is slow

**Info**: First time running downloads ~500MB transformer model. This is normal and happens once.

### WebSocket connection fails

**Fix**: Make sure backend is running on port 8000:
```bash
curl http://localhost:8000/api/health
```

## For Your College Presentation

### Demo Flow

1. **Show the landing page**
   - Explain the project purpose
   - Show the clean UI

2. **Connect as User 1**
   - Send a polite message
   - Show low toxicity score
   - Show intent classification

3. **Send a toxic message**
   - Show high toxicity score (70%+)
   - Show toxic categories (insult, threat, etc.)
   - Show coaching message
   - Click "Show Polite Rewrite"
   - Copy the suggested rewrite

4. **Open second browser**
   - Connect as User 2
   - Show real-time messaging
   - Both users see messages instantly

5. **Show statistics panel**
   - Total messages
   - Toxicity rate
   - Intent breakdown
   - Tone breakdown

6. **Show API documentation**
   - Open http://localhost:8000/docs
   - Show FastAPI automatic documentation
   - Demo a REST API call

### Key Points to Mention

✅ **Real-time processing** using WebSockets  
✅ **AI-powered** with HuggingFace transformers  
✅ **Multi-class detection**: toxicity, intent, tone  
✅ **Practical coaching** with rewrite suggestions  
✅ **Full-stack**: Python backend + React frontend  
✅ **Production-ready**: Database, REST API, WebSockets  

### Technical Highlights

- **Backend**: FastAPI (async Python) + SQLAlchemy ORM
- **ML Model**: unitary/toxic-bert (938M parameters)
- **Database**: PostgreSQL/SQLite with migrations
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS
- **Real-time**: WebSocket bidirectional communication

## Stopping the Servers

### Backend
Press `Ctrl+C` in the terminal running the backend

### Frontend
Press `Ctrl+C` in the terminal running the frontend

## Quick Reference

### Backend URLs
- Health: http://localhost:8000/api/health
- API Docs: http://localhost:8000/docs
- Stats: http://localhost:8000/api/stats

### Frontend URL
- Chat UI: http://localhost:3000

### Test Messages

**Clean Messages:**
```
Hello everyone!
What time is the meeting?
Thank you for your help!
I appreciate your perspective
```

**Toxic Messages (for testing):**
```
You're an idiot
Shut up and listen
This is complete garbage
I hate this stupid idea
```

## Next Steps

1. ✅ Test all features locally
2. 📝 Prepare presentation slides
3. 🎥 Record demo video (backup)
4. 📊 Review statistics dashboard
5. 🚀 Optional: Deploy to Railway/Render

## Need Help?

Check the full documentation:
- Main README: `../README.md`
- API Docs: `../docs/API.md`
- Deployment: `../docs/DEPLOYMENT.md`
- Datasets: `../datasets/README.md`

## Pro Tips

🔥 **Open DevTools** (F12) to show WebSocket messages in Network tab  
🔥 **Show the database** - it stores everything in SQLite  
🔥 **Mention scalability** - can add more rooms, authentication, etc.  
🔥 **Show the code** - clean, well-documented, production-ready  

---

Good luck with your college project! 🎓✨
