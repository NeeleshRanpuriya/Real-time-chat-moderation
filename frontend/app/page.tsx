'use client'

import { useState, useEffect, useRef } from 'react'
import ChatMessage from './components/ChatMessage'
import MessageInput from './components/MessageInput'
import AnalysisPanel from './components/AnalysisPanel'
import StatsPanel from './components/StatsPanel'

interface Message {
  id?: number
  username: string
  message: string
  timestamp: string
  is_toxic?: boolean
  toxicity_score?: number
  type?: string
}

interface Analysis {
  toxicity: {
    score: number
    is_toxic: boolean
    categories: Record<string, number>
    top_categories: string[]
  }
  intent: {
    type: string
    confidence: number
    explanation: string
  }
  tone: {
    type: string
    confidence: number
    explanation: string
  }
}

interface Coaching {
  message: string | null
  suggested_rewrite: string | null
}

export default function Home() {
  const [username, setUsername] = useState('')
  const [isConnected, setIsConnected] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [currentAnalysis, setCurrentAnalysis] = useState<Analysis | null>(null)
  const [currentCoaching, setCurrentCoaching] = useState<Coaching | null>(null)
  const [ws, setWs] = useState<WebSocket | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
  const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'

  useEffect(() => {
    // Scroll to bottom when new messages arrive
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const connectWebSocket = () => {
    if (!username.trim()) {
      alert('Please enter a username')
      return
    }

    const websocket = new WebSocket(`${WS_URL}/ws/${username}`)

    websocket.onopen = () => {
      console.log('✅ WebSocket connected')
      setIsConnected(true)
      setWs(websocket)
    }

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log('📥 Received:', data)

      if (data.type === 'system') {
        setMessages(prev => [...prev, {
          username: 'System',
          message: data.message,
          timestamp: data.timestamp,
          type: 'system'
        }])
      } else if (data.type === 'message') {
        setMessages(prev => [...prev, {
          id: data.id,
          username: data.username,
          message: data.message,
          timestamp: data.timestamp,
          is_toxic: data.is_toxic,
          toxicity_score: data.toxicity_score
        }])
      } else if (data.type === 'analysis') {
        // This is the analysis for our own message
        setCurrentAnalysis(data.analysis)
        setCurrentCoaching(data.coaching)
      }
    }

    websocket.onclose = () => {
      console.log('❌ WebSocket disconnected')
      setIsConnected(false)
      setWs(null)
    }

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error)
      alert('Connection error. Please check if the backend is running.')
    }
  }

  const sendMessage = (message: string) => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ message }))
    }
  }

  const disconnect = () => {
    if (ws) {
      ws.close()
    }
    setIsConnected(false)
    setMessages([])
    setCurrentAnalysis(null)
    setCurrentCoaching(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="max-w-7xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🛡️ Real-Time Chat Moderation
          </h1>
          <p className="text-gray-600">
            AI-powered toxicity detection • Intent classification • Communication coaching
          </p>
        </header>

        {!isConnected ? (
          <div className="max-w-md mx-auto bg-white rounded-lg shadow-lg p-8">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800">Join Chat</h2>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && connectWebSocket()}
              placeholder="Enter your username"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent mb-4"
            />
            <button
              onClick={connectWebSocket}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
            >
              Connect to Chat
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Main Chat Area */}
            <div className="lg:col-span-2 bg-white rounded-lg shadow-lg p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-gray-800">
                  Chat Room <span className="text-green-600">● Live</span>
                </h2>
                <button
                  onClick={disconnect}
                  className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition"
                >
                  Disconnect
                </button>
              </div>

              {/* Messages Container */}
              <div className="chat-container overflow-y-auto mb-4 border border-gray-200 rounded-lg p-4 bg-gray-50">
                {messages.length === 0 ? (
                  <div className="text-center text-gray-500 mt-10">
                    <p>No messages yet. Start the conversation!</p>
                  </div>
                ) : (
                  messages.map((msg, index) => (
                    <ChatMessage key={index} message={msg} currentUser={username} />
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Message Input */}
              <MessageInput onSend={sendMessage} />
            </div>

            {/* Analysis & Stats Panel */}
            <div className="space-y-6">
              <AnalysisPanel analysis={currentAnalysis} coaching={currentCoaching} />
              <StatsPanel apiUrl={API_URL} />
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="text-center mt-12 text-gray-600">
        <p>🎓 College Project • Real-Time Chat Moderation System</p>
        <p className="text-sm mt-2">
          Built with FastAPI, Next.js, HuggingFace Transformers & OpenAI
        </p>
      </footer>
    </div>
  )
}
