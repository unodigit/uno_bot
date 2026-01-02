import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Send, Minimize2, MessageSquare } from 'lucide-react'
import { useChatStore } from '../stores/chatStore'
import { twMerge } from 'tailwind-merge'

interface ChatWindowProps {
  onClose: () => void
  onMinimize?: () => void
}

export function ChatWindow({ onClose, onMinimize }: ChatWindowProps) {
  const [inputValue, setInputValue] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const {
    messages,
    isLoading,
    isStreaming,
    error,
    sessionId,
    createSession,
    sendMessage,
    clearError,
  } = useChatStore()

  // Create session on mount if not exists
  useEffect(() => {
    if (!sessionId) {
      createSession()
    }
  }, [sessionId, createSession])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!inputValue.trim() || isStreaming) return

    const content = inputValue.trim()
    setInputValue('')

    try {
      await sendMessage(content)
    } catch (err) {
      console.error('Failed to send message:', err)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        transition={{ duration: 0.2 }}
        className="fixed bottom-6 right-6 w-[380px] h-[520px] bg-white rounded-lg shadow-xl flex flex-col overflow-hidden z-50"
      >
        {/* Header */}
        <div className="h-12 bg-primary text-white flex items-center justify-between px-4 rounded-t-lg">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
              <span className="text-xs font-bold">UD</span>
            </div>
            <span className="font-semibold text-sm">UnoBot</span>
          </div>
          <div className="flex items-center gap-2">
            {onMinimize && (
              <button
                onClick={onMinimize}
                className="p-1 hover:bg-white/20 rounded transition-colors"
                aria-label="Minimize"
              >
                <Minimize2 className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={onClose}
              className="p-1 hover:bg-white/20 rounded transition-colors"
              aria-label="Close chat"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="bg-error/10 border-b border-error/20 px-4 py-2 flex items-center justify-between">
            <span className="text-xs text-error">{error}</span>
            <button onClick={clearError} className="text-error hover:opacity-70 text-xs font-bold">✕</button>
          </div>
        )}

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50">
          {messages.length === 0 && !isLoading && (
            <div className="flex justify-center items-center h-full text-text-muted text-sm">
              <div className="text-center">
                <div className="animate-pulse mb-2">...</div>
                <p>Initializing chat...</p>
              </div>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={twMerge(
                'flex w-full',
                message.role === 'user' ? 'justify-end' : 'justify-start'
              )}
            >
              <div
                className={twMerge(
                  'max-w-[85%] rounded-lg px-3 py-2 text-sm shadow-sm',
                  message.role === 'user'
                    ? 'bg-primary text-white rounded-br-none'
                    : 'bg-white text-text border border-border rounded-bl-none'
                )}
              >
                <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                <span className={twMerge(
                  'text-[10px] opacity-70 mt-1 block',
                  message.role === 'user' ? 'text-white/80' : 'text-text-muted'
                )}>
                  {formatTime(message.created_at)}
                </span>
              </div>
            </div>
          ))}

          {/* Typing Indicator */}
          {isStreaming && (
            <div className="flex justify-start">
              <div className="bg-white border border-border rounded-lg px-3 py-2 shadow-sm">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-text-muted rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-text-muted rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                  <div className="w-2 h-2 bg-text-muted rounded-full animate-bounce" style={{ animationDelay: '0.4s' }} />
                </div>
              </div>
            </div>
          )}

          {/* Loading State */}
          {isLoading && messages.length === 0 && (
            <div className="flex justify-center items-center h-full">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="h-14 border-t border-border bg-white p-3 flex items-center gap-2 rounded-b-lg">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isStreaming ? 'Bot is typing...' : 'Type your message...'}
            className="flex-1 h-full px-3 border border-border rounded-md focus:outline-none focus:ring-2 focus:ring-primary text-sm disabled:opacity-50"
            disabled={isStreaming || isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!inputValue.trim() || isStreaming || isLoading}
            className="h-full px-4 bg-primary hover:bg-primary-dark disabled:bg-opacity-50 disabled:cursor-not-allowed text-white rounded-md transition-colors flex items-center justify-center"
            aria-label="Send message"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
