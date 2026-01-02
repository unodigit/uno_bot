import { useState } from 'react'
import { MessageSquare } from 'lucide-react'
import { ChatWindow } from './ChatWindow'

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [messageCount, setMessageCount] = useState(0)

  const handleOpen = () => {
    setIsOpen(true)
    setIsMinimized(false)
  }

  const handleClose = () => {
    setIsOpen(false)
    setMessageCount(0)
  }

  const handleMinimize = () => {
    setIsOpen(false)
    setIsMinimized(true)
    setMessageCount(prev => Math.max(prev, 1))
  }

  return (
    <>
      {/* Floating Button - Normal */}
      {!isOpen && !isMinimized && (
        <button
          onClick={handleOpen}
          className="fixed bottom-6 right-6 w-[60px] h-[60px] bg-primary hover:bg-primary-dark rounded-full shadow-lg flex items-center justify-center transition-all duration-300 hover:scale-110 z-50"
          aria-label="Open chat"
        >
          <MessageSquare className="w-8 h-8 text-white" />
        </button>
      )}

      {/* Floating Button - Minimized with Badge */}
      {!isOpen && isMinimized && (
        <button
          onClick={handleOpen}
          className="fixed bottom-6 right-6 w-[60px] h-[60px] bg-primary hover:bg-primary-dark rounded-full shadow-lg flex items-center justify-center transition-all duration-300 hover:scale-110 relative z-50"
          aria-label="Open chat"
        >
          <MessageSquare className="w-8 h-8 text-white" />
          <span className="absolute -top-1 -right-1 w-6 h-6 bg-red-500 text-white text-xs font-bold rounded-full flex items-center justify-center border-2 border-white">
            {messageCount}
          </span>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <ChatWindow
          onClose={handleClose}
          onMinimize={handleMinimize}
        />
      )}
    </>
  )
}
