interface Message {
  username: string
  message: string
  timestamp: string
  is_toxic?: boolean
  toxicity_score?: number
  type?: string
}

interface ChatMessageProps {
  message: Message
  currentUser: string
}

export default function ChatMessage({ message, currentUser }: ChatMessageProps) {
  const isOwnMessage = message.username === currentUser
  const isSystem = message.type === 'system'
  
  if (isSystem) {
    return (
      <div className="text-center text-gray-500 text-sm my-2">
        <span className="bg-gray-200 px-3 py-1 rounded-full">
          {message.message}
        </span>
      </div>
    )
  }

  const getToxicityBadge = () => {
    if (!message.is_toxic) return null
    
    const score = message.toxicity_score || 0
    
    if (score > 0.7) {
      return (
        <span className="toxic-badge badge-toxic ml-2">
          ⚠️ High Toxicity
        </span>
      )
    } else if (score > 0.5) {
      return (
        <span className="toxic-badge badge-warning ml-2">
          ⚡ Moderate
        </span>
      )
    }
    return null
  }

  return (
    <div className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'} mb-3`}>
      <div className={`max-w-md ${isOwnMessage ? 'order-2' : 'order-1'}`}>
        <div className="flex items-baseline mb-1">
          <span className={`text-sm font-semibold ${isOwnMessage ? 'text-blue-600' : 'text-gray-700'}`}>
            {message.username}
          </span>
          {getToxicityBadge()}
        </div>
        <div
          className={`message-bubble ${
            isOwnMessage
              ? 'bg-blue-500 text-white'
              : message.is_toxic
              ? 'bg-red-100 text-red-900 border-2 border-red-300'
              : 'bg-white text-gray-800 border border-gray-200'
          }`}
        >
          <p className="break-words">{message.message}</p>
        </div>
        <span className="text-xs text-gray-500 mt-1">
          {new Date(message.timestamp).toLocaleTimeString()}
        </span>
      </div>
    </div>
  )
}
