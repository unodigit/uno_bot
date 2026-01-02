import { useState, useEffect, useRef } from 'react'
import { MessageSquare, ArrowLeft, ArrowRight } from 'lucide-react'
import { ChatWindow } from './ChatWindow'
import { useChatStore } from '../stores/chatStore'

export function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [isFirstVisit, setIsFirstVisit] = useState(false)
  const [showPositionMenu, setShowPositionMenu] = useState(false)

  // Ref for the main chat button to restore focus when closing
  const buttonRef = useRef<HTMLButtonElement>(null)

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
      // Return focus to the button after closing
      setTimeout(() => {
        buttonRef.current?.focus()
      }, 100)
    }
  }

  const handleMinimize = () => {
    setIsMinimized(true)
    setIsOpen(false)
    // Return focus to the button after minimizing
    setTimeout(() => {
      buttonRef.current?.focus()
    }, 100)
  }

  // Handle keyboard navigation for position menu
  const handlePositionMenuKeyDown = (e: React.KeyboardEvent, position: 'left' | 'right') => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault()
      setWidgetPosition(position)
      setShowPositionMenu(false)
      buttonRef.current?.focus()
    } else if (e.key === 'Escape') {
      setShowPositionMenu(false)
      buttonRef.current?.focus()
    }
  }

  // Handle mouse enter/leave for position menu with keyboard support
  const handleMouseEnter = () => setShowPositionMenu(true)
  const handleMouseLeave = () => setShowPositionMenu(false)

  const unreadCount = messages.filter(m => m.role === 'assistant').length

  return (
    <>
      {/* Screen reader announcements */}
      <div aria-live="polite" aria-atomic="true" className="sr-only">
        {isFirstVisit && "Chat widget loaded. Press Enter to open chat."}
        {isOpen && "Chat window opened."}
        {!isOpen && isMinimized && `Chat minimized. ${unreadCount} new messages.`}
        {showPositionMenu && "Position menu opened. Use arrow keys or tab to select position."}
      </div>

      {/* Position Toggle Menu - appears on hover of button area */}
      {!isOpen && !isMinimized && showPositionMenu && (
        <div className={`fixed bottom-24 ${position.menu} bg-white dark:bg-gray-800 rounded-lg shadow-xl p-2 flex gap-2 z-50 border border-gray-200 dark:border-gray-700`}
             role="menu"
             aria-label="Widget position options">
          <button
            onClick={() => { setWidgetPosition('left'); setShowPositionMenu(false); buttonRef.current?.focus(); }}
            onKeyDown={(e) => handlePositionMenuKeyDown(e, 'left')}
            className={`p-2 rounded ${widgetPosition === 'left' ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 focus:ring-2 focus:ring-primary focus:outline-none'}`}
            aria-label="Position on left"
            aria-pressed={widgetPosition === 'left'}
            data-testid="position-left"
            tabIndex={0}
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <button
            onClick={() => { setWidgetPosition('right'); setShowPositionMenu(false); buttonRef.current?.focus(); }}
            onKeyDown={(e) => handlePositionMenuKeyDown(e, 'right')}
            className={`p-2 rounded ${widgetPosition === 'right' ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 focus:ring-2 focus:ring-primary focus:outline-none'}`}
            aria-label="Position on right"
            aria-pressed={widgetPosition === 'right'}
            data-testid="position-right"
            tabIndex={0}
          >
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Floating Button - Normal */}
      {!isOpen && !isMinimized && (
        <div className="group">
          <button
            ref={buttonRef}
            onClick={handleToggle}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                handleToggle()
              } else if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
                // Open position menu with arrow keys
                e.preventDefault()
                setShowPositionMenu(true)
              } else if (e.key === 'Escape' && showPositionMenu) {
                // Close position menu with Escape
                e.preventDefault()
                setShowPositionMenu(false)
              }
            }}
            className={`fixed ${position.button} w-[60px] h-[60px] bg-primary hover:bg-primary-dark text-white rounded-full shadow-lg flex items-center justify-center transition-all duration-300 hover:scale-110 z-50 ${isFirstVisit ? 'animate-pulse-subtle' : ''} focus:ring-2 focus:ring-white focus:outline-none`}
            aria-label="Open chat"
            aria-expanded={isOpen}
            aria-haspopup="menu"
            aria-describedby="chat-widget-tooltip"
            data-testid="chat-widget-button"
            tabIndex={0}
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
            ref={buttonRef}
            onClick={handleToggle}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            onKeyDown={(e) => {
              if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault()
                handleToggle()
              } else if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
                // Open position menu with arrow keys
                e.preventDefault()
                setShowPositionMenu(true)
              } else if (e.key === 'Escape' && showPositionMenu) {
                // Close position menu with Escape
                e.preventDefault()
                setShowPositionMenu(false)
              }
            }}
            className={`fixed ${position.button} w-[60px] h-[60px] bg-primary hover:bg-primary-dark text-white rounded-full shadow-lg flex items-center justify-center transition-all duration-300 hover:scale-110 relative z-50 focus:ring-2 focus:ring-white focus:outline-none`}
            aria-label={`Open chat. ${unreadCount} new messages`}
            aria-expanded={isOpen}
            aria-haspopup="menu"
            aria-describedby="chat-widget-tooltip-minimized"
            data-testid="chat-widget-button-minimized"
            tabIndex={0}
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
                onClick={() => { setWidgetPosition('left'); setShowPositionMenu(false); buttonRef.current?.focus(); }}
                onKeyDown={(e) => handlePositionMenuKeyDown(e, 'left')}
                className={`p-2 rounded ${widgetPosition === 'left' ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 focus:ring-2 focus:ring-primary focus:outline-none'}`}
                aria-label="Position on left"
                aria-pressed={widgetPosition === 'left'}
                data-testid="position-left"
                tabIndex={0}
              >
                <ArrowLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => { setWidgetPosition('right'); setShowPositionMenu(false); buttonRef.current?.focus(); }}
                onKeyDown={(e) => handlePositionMenuKeyDown(e, 'right')}
                className={`p-2 rounded ${widgetPosition === 'right' ? 'bg-primary text-white' : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 focus:ring-2 focus:ring-primary focus:outline-none'}`}
                aria-label="Position on right"
                aria-pressed={widgetPosition === 'right'}
                data-testid="position-right"
                tabIndex={0}
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
          onClose={() => {
            setIsOpen(false)
            // Return focus to button
            setTimeout(() => {
              buttonRef.current?.focus()
            }, 100)
          }}
          onMinimize={handleMinimize}
        />
      )}
    </>
  )
}
