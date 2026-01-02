import { useState, useEffect } from 'react'
import { MessageSquare } from 'lucide-react'
import { ChatWindow } from './ChatWindow'
import { useChatStore } from '../stores/chatStore'

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)

  const { messages, sessionId, createSession } = useChatStore()

  // Check for existing session on mount
  useEffect(() => {
    const existingSessionId = localStorage.getItem('unobot_session_id')
    if (existingSessionId) {
      createSession()
    }
  }, [createSession])

  const handleToggle = () => {
    if (!isOpen) {
      setIsOpen(true)
      setIsMinimized(false)
      // Initialize session on first open
      if (!sessionId) {
        createSession()
      }
    } else {
      setIsOpen(false)
    }
  }

  const handleMinimize = () => {
    setIsMinimized(true)
    setIsOpen(false)
  }

  const unreadCount = messages.filter(m => m.role === 'assistant').length

  return (
    <>
      {/* Floating Button - Normal */}
      {!isOpen && !isMinimized && (
        <button
          onClick={handleToggle}
          className="fixed bottom-6 right-6 w-[60px] h-[60px] bg-primary hover:bg-primary-dark text-white rounded-full shadow-lg flex items-center justify-center transition-all duration-300 hover:scale-110 z-50"
          aria-label="Open chat"
          data-testid="chat-widget-button"
        >
          <MessageSquare className="w-8 h-8" />
        </button>
      )}

      {/* Floating Button - Minimized with Unread Badge */}
      {!isOpen && isMinimized && (
        <button
          onClick={handleToggle}
          className="fixed bottom-6 right-6 w-[60px] h-[60px] bg-primary hover:bg-primary-dark text-white rounded-full shadow-lg flex items-center justify-center transition-all duration-300 hover:scale-110 relative z-50"
          aria-label="Open chat"
          data-testid="chat-widget-button-minimized"
        >
          <MessageSquare className="w-8 h-8" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 w-6 h-6 bg-error text-white text-xs font-bold rounded-full flex items-center justify-center border-2 border-white">
              {unreadCount}
            </span>
          )}
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <ChatWindow
          onClose={() => setIsOpen(false)}
          onMinimize={handleMinimize}
        />
      )}
    </>
  )
}
