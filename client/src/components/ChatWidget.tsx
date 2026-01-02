import { useState, useEffect } from 'react'
import { MessageSquare, ArrowLeft, ArrowRight } from 'lucide-react'
import { ChatWindow } from './ChatWindow'
import { useChatStore } from '../stores/chatStore'

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [isFirstVisit, setIsFirstVisit] = useState(false)
  const [showPositionMenu, setShowPositionMenu] = useState(false)

  const { messages, sessionId, createSession, loadSession, widgetPosition, setWidgetPosition } = useChatStore()

  // Helper to get position classes based on widgetPosition
  const getPositionClasses = () => {
    if (widgetPosition === 'left') {
      return {
        button: 'bottom-6 left-6',
        badge: '-top-1 -left-1',
        menu: 'left-6'
      }
    }
    // Default to right
    return {
      button: 'bottom-6 right-6',
      badge: '-top-1 -right-1',
      menu: 'right-6'
    }
  }

  const position = getPositionClasses()

  // Check for existing session on mount and determine if first visit
  useEffect(() => {
    const existingSessionId = localStorage.getItem('unobot_session_id')
    const hasSeenWidget = localStorage.getItem('unobot_widget_seen')

    // Check if this is the first time seeing the widget
    if (!hasSeenWidget) {
      setIsFirstVisit(true)
      // Mark as seen after 3 seconds
      const timer = setTimeout(() => {
        setIsFirstVisit(false)
        localStorage.setItem('unobot_widget_seen', 'true')
      }, 3000)
      return () => clearTimeout(timer)
    }

    if (existingSessionId && !sessionId) {
      // Load existing session instead of creating a new one
      loadSession(existingSessionId)
    }
  }, [sessionId, loadSession])

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
      {/* Screen reader announcements */}
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {isFirstVisit && "Chat widget loaded. Press Enter to open chat."}
        {isOpen && "Chat window opened."}
        {!isOpen && isMinimized && `Chat minimized. ${unreadCount} new messages.`}
      </div>

      {/* Position Toggle Menu - appears on hover of button area */}
      {!isOpen && !isMinimized && showPositionMenu && (
        <div className={`fixed bottom-24 ${position.menu} bg-white dark:bg-gray-800 rounded-lg shadow-xl p-2 flex gap-2 z-50 border border-gray-200 dark:border-gray-700`}
             role="menu"
             aria-label="Widget position options">
          <button
            onClick={() => setWidgetPosition('left')}
            className={`p-2 rounded ${widgetPosition === 'left' ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600'}`}
            aria-label="Position on left"
            aria-pressed={widgetPosition === 'left'}
            data-testid="position-left"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <button
            onClick={() => setWidgetPosition('right')}
            className={`p-2 rounded ${widgetPosition === 'right' ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600'}`}
            aria-label="Position on right"
            aria-pressed={widgetPosition === 'right'}
            data-testid="position-right"
          >
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Floating Button - Normal */}
      {!isOpen && !isMinimized && (
        <div className="group">
          <button
            onClick={handleToggle}
            onMouseEnter={() => setShowPositionMenu(true)}
            onMouseLeave={() => setShowPositionMenu(false)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                handleToggle()
              }
            }}
            className={`fixed ${position.button} w-[60px] h-[60px] bg-primary hover:bg-primary-dark text-white rounded-full shadow-lg flex items-center justify-center transition-all duration-300 hover:scale-110 z-50 ${isFirstVisit ? 'animate-pulse-subtle' : ''}`}
            aria-label="Open chat"
            aria-expanded={isOpen}
            aria-describedby="chat-widget-tooltip"
            data-testid="chat-widget-button"
          >
            <MessageSquare className="w-8 h-8" />
            <span id="chat-widget-tooltip" className="sr-only">UnoBot - AI Business Consultant</span>
          </button>
        </div>
      )}

      {/* Floating Button - Minimized with Unread Badge */}
      {!isOpen && isMinimized && (
        <div className="group">
          <button
            onClick={handleToggle}
            onMouseEnter={() => setShowPositionMenu(true)}
            onMouseLeave={() => setShowPositionMenu(false)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                handleToggle()
              }
            }}
            className={`fixed ${position.button} w-[60px] h-[60px] bg-primary hover:bg-primary-dark text-white rounded-full shadow-lg flex items-center justify-center transition-all duration-300 hover:scale-110 relative z-50`}
            aria-label={`Open chat. ${unreadCount} new messages`}
            aria-expanded={isOpen}
            aria-describedby="chat-widget-tooltip-minimized"
            data-testid="chat-widget-button-minimized"
          >
            <MessageSquare className="w-8 h-8" />
            <span id="chat-widget-tooltip-minimized" className="sr-only">UnoBot - AI Business Consultant</span>
            {unreadCount > 0 && (
              <span className={`absolute ${position.badge} w-6 h-6 bg-error text-white text-xs font-bold rounded-full flex items-center justify-center border-2 border-white`} aria-label={`${unreadCount} unread messages`}>
                {unreadCount}
              </span>
            )}
          </button>
          {/* Position menu for minimized button */}
          {showPositionMenu && (
            <div className={`fixed bottom-24 ${position.menu} bg-white dark:bg-gray-800 rounded-lg shadow-xl p-2 flex gap-2 z-50 border border-gray-200 dark:border-gray-700`}
                 role="menu"
                 aria-label="Widget position options">
              <button
                onClick={() => setWidgetPosition('left')}
                className={`p-2 rounded ${widgetPosition === 'left' ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600'}`}
                aria-label="Position on left"
                aria-pressed={widgetPosition === 'left'}
                data-testid="position-left"
              >
                <ArrowLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => setWidgetPosition('right')}
                className={`p-2 rounded ${widgetPosition === 'right' ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600'}`}
                aria-label="Position on right"
                aria-pressed={widgetPosition === 'right'}
                data-testid="position-right"
              >
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
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
