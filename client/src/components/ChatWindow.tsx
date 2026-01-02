import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Send, Minimize2, MessageSquare, Download, FileText, ExternalLink } from 'lucide-react'
import { useChatStore } from '../stores/chatStore'
import { twMerge } from 'tailwind-merge'

interface ChatWindowProps {
  onClose: () => void
  onMinimize?: () => void
}

// Phase-based quick reply options
const getQuickReplies = (phase: string, context: any): string[] => {
  switch (phase) {
    case 'greeting':
      return ['Hi!', 'Hello', "I'm interested", 'Need help'];
    case 'discovery':
      return ['Email: test@example.com', 'I work at Acme Corp', 'Tech industry', 'Healthcare'];
    case 'qualification':
      return ['Budget: $25k-$100k', 'Budget: Under $25k', 'Timeline: 1-3 months', 'Timeline: Urgent'];
    default:
      return ['Yes', 'No', 'Tell me more', 'Next'];
  }
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
    currentPhase,
    clientInfo,
    businessContext,
    qualification,
    prdPreview,
    isGeneratingPRD,
    generatePRD,
    downloadPRD,
    clearPRDPreview,
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
      // Check if this is a special PRD generation request
      if (content === 'Generate PRD') {
        await generatePRD()
        // Add user message
        await sendMessage(content)
      } else {
        await sendMessage(content)
      }
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

  const handleGeneratePRD = async () => {
    try {
      await generatePRD()
    } catch (err) {
      console.error('Failed to generate PRD:', err)
    }
  }

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  // Check if session has enough data for PRD generation
  const canGeneratePRD = () => {
    return (
      sessionId &&
      clientInfo?.name &&
      businessContext?.challenges &&
      !isGeneratingPRD
    )
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, scale: 0.9, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.9, y: 20 }}
        transition={{ duration: 0.2 }}
        className="fixed bottom-6 right-6 w-[380px] h-[520px] bg-white rounded-lg shadow-xl flex flex-col overflow-hidden z-50"
        data-testid="chat-window"
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
                data-testid="minimize-button"
              >
                <Minimize2 className="w-4 h-4" />
              </button>
            )}
            <button
              onClick={onClose}
              className="p-1 hover:bg-white/20 rounded transition-colors"
              aria-label="Close chat"
              data-testid="close-button"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* PRD Preview Card */}
        {prdPreview && (
          <div className="mx-3 mt-3 p-3 bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg shadow-sm" data-testid="prd-preview-card">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center flex-shrink-0">
                <FileText className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <h4 className="text-sm font-semibold text-gray-900">PRD Generated!</h4>
                  <button
                    onClick={clearPRDPreview}
                    className="text-xs text-blue-600 hover:text-blue-800 underline"
                  >
                    Hide
                  </button>
                </div>
                <p className="text-xs text-gray-600 mb-2 line-clamp-2">{prdPreview.preview_text}</p>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => prdPreview.id && downloadPRD(prdPreview.id)}
                    className="flex items-center gap-1 px-2 py-1 bg-primary hover:bg-primary-dark text-white text-xs rounded transition-colors"
                    data-testid="download-prd-button"
                  >
                    <Download className="w-3 h-3" />
                    Download
                  </button>
                  <span className="text-xs text-gray-500">{prdPreview.filename}</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* PRD Generation Indicator */}
        {isGeneratingPRD && (
          <div className="mx-3 mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg" data-testid="prd-generating">
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
              <span className="text-xs text-blue-700">Generating PRD...</span>
            </div>
          </div>
        )}

        {/* Error Banner */}
        {error && (
          <div className="bg-error/10 border-b border-error/20 px-4 py-2 flex items-center justify-between">
            <span className="text-xs text-error">{error}</span>
            <button onClick={clearError} className="text-error hover:opacity-70 text-xs font-bold">✕</button>
          </div>
        )}

        {/* Messages Area */}
        <div
          className="flex-1 overflow-y-auto p-4 space-y-3 bg-gray-50"
          data-testid="messages-container"
        >
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
              data-testid={`message-${message.role}`}
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
            <div className="flex justify-start" data-testid="typing-indicator">
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
            <div className="flex justify-center items-center h-full" data-testid="loading-indicator">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Generate PRD Button */}
        {!isStreaming && !isLoading && messages.length > 0 && !prdPreview && !isGeneratingPRD && (
          <div className="px-3 pb-2 bg-white border-t border-border" data-testid="prd-actions">
            <button
              onClick={handleGeneratePRD}
              disabled={!canGeneratePRD()}
              className={twMerge(
                'w-full py-2 px-3 rounded-md transition-colors flex items-center justify-center gap-2 text-sm font-medium',
                canGeneratePRD()
                  ? 'bg-blue-600 hover:bg-blue-700 text-white'
                  : 'bg-gray-200 text-gray-500 cursor-not-allowed'
              )}
              data-testid="generate-prd-button"
            >
              <FileText className="w-4 h-4" />
              Generate PRD
            </button>
            {!canGeneratePRD() && (
              <div className="text-[10px] text-gray-500 mt-1 text-center">
                Complete the conversation to enable PRD generation
              </div>
            )}
          </div>
        )}

        {/* Quick Reply Buttons */}
        {!isStreaming && !isLoading && messages.length > 0 && !prdPreview && !isGeneratingPRD && (
          <div className="px-3 pb-2 bg-white border-t border-border" data-testid="quick-replies">
            <div className="flex flex-wrap gap-2 mb-2">
              {getQuickReplies(currentPhase, { clientInfo, businessContext, qualification }).map((reply, idx) => (
                <button
                  key={idx}
                  onClick={() => sendMessage(reply)}
                  className="px-3 py-1.5 text-xs bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full transition-colors border border-gray-300"
                  disabled={isStreaming || isLoading}
                >
                  {reply}
                </button>
              ))}
            </div>
          </div>
        )}

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
            data-testid="message-input"
          />
          <button
            onClick={handleSend}
            disabled={!inputValue.trim() || isStreaming || isLoading}
            className="h-full px-4 bg-primary hover:bg-primary-dark disabled:bg-opacity-50 disabled:cursor-not-allowed text-white rounded-md transition-colors flex items-center justify-center"
            aria-label="Send message"
            data-testid="send-button"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
