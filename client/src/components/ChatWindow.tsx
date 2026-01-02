import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Send, Minimize2, MessageSquare, Download, FileText, ExternalLink, UserPlus, ArrowLeft, Calendar, Check, XCircle, RefreshCw } from 'lucide-react'
import { useChatStore } from '../stores/chatStore'
import { twMerge } from 'tailwind-merge'
import { ExpertMatchList } from './ExpertCard'
import { CalendarPicker } from './CalendarPicker'
import { BookingForm } from './BookingForm'
import { BookingConfirmation } from './BookingConfirmation'
import { TimeSlot } from '../types'

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
    case 'expert_matching':
      return ['Match Experts', 'Show me experts', 'Get recommendations'];
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
    matchedExperts,
    isMatchingExperts,
    matchExperts,
    clearMatchedExperts,
    // Summary state
    conversationSummary,
    isGeneratingSummary,
    isReviewingSummary,
    // Summary actions
    generateSummary,
    approveSummary,
    rejectSummary,
    clearSummary,
    // Booking flow state
    bookingState,
    selectedExpert,
    selectedTimeSlot,
    createdBooking,
    isCreatingBooking,
    isCancellingBooking,
    // Booking flow actions
    startBookingFlow,
    selectTimeSlot,
    confirmBooking,
    cancelBooking,
    resetBookingFlow,
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
        // Start summary flow instead of direct PRD generation
        await generateSummary()
        // Add user message
        await sendMessage(content)
      } else if (content.toLowerCase().includes('match') || content.toLowerCase().includes('expert') || content.toLowerCase().includes('recommend')) {
        // Trigger expert matching
        await matchExperts()
        // Also send the message for conversation history
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
      // Start the summary flow instead of direct PRD generation
      await generateSummary()
    } catch (err) {
      console.error('Failed to generate summary:', err)
    }
  }

  const handleMatchExperts = async () => {
    try {
      await matchExperts()
    } catch (err) {
      console.error('Failed to match experts:', err)
    }
  }

  const handleSelectExpert = (expert: any) => {
    // Send a message about selecting the expert
    sendMessage(`I'd like to work with ${expert.name} (${expert.role})`)
  }

  const handleBookExpert = (expert: any) => {
    startBookingFlow(expert)
  }

  const handleTimeSlotSelect = async (slot: TimeSlot) => {
    try {
      await selectTimeSlot(slot)
    } catch (err) {
      console.error('Failed to select time slot:', err)
    }
  }

  const handleBookingSubmit = async (name: string, email: string) => {
    try {
      await confirmBooking(name, email)
    } catch (err) {
      console.error('Failed to confirm booking:', err)
    }
  }

  const handleBookingDone = () => {
    resetBookingFlow()
    clearMatchedExperts()
  }

  const handleApproveSummary = async () => {
    try {
      await approveSummary()
    } catch (err) {
      console.error('Failed to approve summary:', err)
    }
  }

  const handleRejectSummary = async () => {
    try {
      await rejectSummary()
    } catch (err) {
      console.error('Failed to reject summary:', err)
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
      !isGeneratingPRD &&
      !isGeneratingSummary
    )
  }

  // Check if session has enough data for expert matching
  const canMatchExperts = () => {
    return (
      sessionId &&
      businessContext?.challenges &&
      !isMatchingExperts
    )
  }

  // Booking flow UI
  if (bookingState === 'selecting_time' && selectedExpert) {
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
              <span className="font-semibold text-sm">Book Appointment</span>
            </div>
            <button
              onClick={onClose}
              className="p-1 hover:bg-white/20 rounded transition-colors"
              aria-label="Close chat"
              data-testid="close-button"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="bg-error/10 border-b border-error/20 px-4 py-2 flex items-center justify-between">
              <span className="text-xs text-error">{error}</span>
              <button onClick={clearError} className="text-error hover:opacity-70 text-xs font-bold">✕</button>
            </div>
          )}

          {/* Content Area */}
          <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
            <CalendarPicker
              expertId={selectedExpert.id}
              expertName={selectedExpert.name}
              onSelectSlot={handleTimeSlotSelect}
              onBack={resetBookingFlow}
            />
          </div>
        </motion.div>
      </AnimatePresence>
    )
  }

  if (bookingState === 'confirming' && selectedExpert && selectedTimeSlot) {
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
              <span className="font-semibold text-sm">Booking Details</span>
            </div>
            <button
              onClick={onClose}
              className="p-1 hover:bg-white/20 rounded transition-colors"
              aria-label="Close chat"
              data-testid="close-button"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="bg-error/10 border-b border-error/20 px-4 py-2 flex items-center justify-between">
              <span className="text-xs text-error">{error}</span>
              <button onClick={clearError} className="text-error hover:opacity-70 text-xs font-bold">✕</button>
            </div>
          )}

          {/* Content Area */}
          <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
            <BookingForm
              expert={selectedExpert}
              timeSlot={selectedTimeSlot}
              onBack={() => {
                // Go back to time selection
                const { selectedTimeSlot: _, ...rest } = {} as any
              }}
              onSubmit={handleBookingSubmit}
              isSubmitting={isCreatingBooking}
              error={error}
            />
          </div>
        </motion.div>
      </AnimatePresence>
    )
  }

  if (bookingState === 'completed' && createdBooking) {
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
              <span className="font-semibold text-sm">Booking Confirmed</span>
            </div>
            <button
              onClick={onClose}
              className="p-1 hover:bg-white/20 rounded transition-colors"
              aria-label="Close chat"
              data-testid="close-button"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Content Area */}
          <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
            <BookingConfirmation
              booking={{
                id: createdBooking.id,
                expert_name: selectedExpert?.name || '',
                expert_role: selectedExpert?.role || '',
                start_time: createdBooking.start_time,
                end_time: createdBooking.end_time,
                timezone: createdBooking.timezone,
                meeting_link: createdBooking.meeting_link,
                client_name: createdBooking.client_name,
                client_email: createdBooking.client_email,
              }}
              onDone={handleBookingDone}
              onCancel={cancelBooking}
              isCancelling={isCancellingBooking}
            />
          </div>
        </motion.div>
      </AnimatePresence>
    )
  }

  // Cancelled booking view
  if (bookingState === 'cancelled') {
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
          <div className="h-12 bg-gray-700 text-white flex items-center justify-between px-4 rounded-t-lg">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
                <span className="text-xs font-bold">UD</span>
              </div>
              <span className="font-semibold text-sm">Booking Cancelled</span>
            </div>
            <button
              onClick={onClose}
              className="p-1 hover:bg-white/20 rounded transition-colors"
              aria-label="Close chat"
              data-testid="close-button"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Content Area */}
          <div className="flex-1 overflow-y-auto p-4 bg-gray-50 flex flex-col items-center justify-center text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
              <X className="w-8 h-8 text-red-600" />
            </div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">Booking Cancelled</h3>
            <p className="text-sm text-gray-600 mb-6">
              Your appointment has been successfully cancelled.
            </p>
            <button
              onClick={() => {
                resetBookingFlow()
                clearMatchedExperts()
              }}
              className="w-full py-2 bg-primary hover:bg-primary-dark text-white rounded-lg font-medium transition-colors"
            >
              Start New Booking
            </button>
          </div>
        </motion.div>
      </AnimatePresence>
    )
  }

  // Summary review UI - this appears BEFORE the normal chat view
  if (isReviewingSummary && conversationSummary) {
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
              <span className="font-semibold text-sm">Review Summary</span>
            </div>
            <button
              onClick={onClose}
              className="p-1 hover:bg-white/20 rounded transition-colors"
              aria-label="Close chat"
              data-testid="close-button"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          {/* Error Banner */}
          {error && (
            <div className="bg-error/10 border-b border-error/20 px-4 py-2 flex items-center justify-between">
              <span className="text-xs text-error">{error}</span>
              <button onClick={clearError} className="text-error hover:opacity-70 text-xs font-bold">✕</button>
            </div>
          )}

          {/* Summary Content */}
          <div className="flex-1 overflow-y-auto p-4 bg-gray-50">
            <div className="bg-gradient-to-br from-purple-50 to-indigo-50 border border-purple-200 rounded-lg p-4 mb-4">
              <div className="flex items-start gap-3 mb-3">
                <div className="w-10 h-10 bg-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
                  <FileText className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h4 className="text-sm font-semibold text-gray-900 mb-1">Conversation Summary</h4>
                  <p className="text-xs text-gray-600 mb-2">
                    Please review this summary of your conversation. It will be included with your PRD.
                  </p>
                </div>
              </div>

              <div className="bg-white rounded-md p-3 border border-purple-200 mb-3">
                <p className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">{conversationSummary}</p>
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handleApproveSummary}
                  disabled={isGeneratingPRD}
                  className={twMerge(
                    'flex-1 py-2 px-3 rounded-md transition-colors flex items-center justify-center gap-2 text-sm font-medium',
                    isGeneratingPRD
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-green-600 hover:bg-green-700 text-white'
                  )}
                  data-testid="approve-summary-button"
                >
                  <Check className="w-4 h-4" />
                  Approve
                </button>
                <button
                  onClick={handleRejectSummary}
                  disabled={isGeneratingSummary}
                  className={twMerge(
                    'flex-1 py-2 px-3 rounded-md transition-colors flex items-center justify-center gap-2 text-sm font-medium',
                    isGeneratingSummary
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-orange-600 hover:bg-orange-700 text-white'
                  )}
                  data-testid="regenerate-summary-button"
                >
                  <RefreshCw className="w-4 h-4" />
                  Regenerate
                </button>
                <button
                  onClick={clearSummary}
                  className="flex-1 py-2 px-3 rounded-md transition-colors flex items-center justify-center gap-2 text-sm font-medium bg-gray-200 hover:bg-gray-300 text-gray-700"
                  data-testid="cancel-summary-button"
                >
                  <XCircle className="w-4 h-4" />
                  Cancel
                </button>
              </div>
            </div>

            {/* Loading indicator for PRD generation */}
            {isGeneratingPRD && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                <div className="flex items-center gap-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                  <span className="text-xs text-blue-700">Generating PRD with approved summary...</span>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </AnimatePresence>
    )
  }

  // Normal chat view
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

        {/* Summary Generation Indicator */}
        {isGeneratingSummary && (
          <div className="mx-3 mt-3 p-3 bg-purple-50 border border-purple-200 rounded-lg" data-testid="summary-generating">
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
              <span className="text-xs text-purple-700">Generating conversation summary...</span>
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

        {/* Expert Matching Indicator */}
        {isMatchingExperts && (
          <div className="mx-3 mt-3 p-3 bg-purple-50 border border-purple-200 rounded-lg" data-testid="expert-matching">
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
              <span className="text-xs text-purple-700">Finding the right experts...</span>
            </div>
          </div>
        )}

        {/* Expert Match List */}
        {matchedExperts.length > 0 && !isMatchingExperts && (
          <div className="mx-3 mt-3 overflow-y-auto max-h-[180px]" data-testid="expert-match-container">
            <ExpertMatchList
              experts={matchedExperts}
              onSelect={handleSelectExpert}
              onBook={handleBookExpert}
              showActions={true}
            />
            <button
              onClick={clearMatchedExperts}
              className="mt-2 text-xs text-gray-500 hover:text-gray-700 underline w-full text-center"
            >
              Hide experts
            </button>
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
            <motion.div
              key={message.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
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
                    ? 'bg-primary text-white rounded-br-sm'
                    : 'bg-gray-100 text-gray-800 rounded-bl-sm border border-gray-200'
                )}
              >
                <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                <span className={twMerge(
                  'text-[10px] opacity-70 mt-1 block',
                  message.role === 'user' ? 'text-white/80' : 'text-gray-600'
                )}>
                  {formatTime(message.created_at)}
                </span>
              </div>
            </motion.div>
          ))}

          {/* Typing Indicator */}
          {isStreaming && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-start"
              data-testid="typing-indicator"
            >
              <div className="bg-surface border border-border rounded-lg rounded-bl-sm px-4 py-3 shadow-sm max-w-[85%]">
                <div className="flex items-center space-x-1">
                  <div className="w-2 h-2 bg-text-muted rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-text-muted rounded-full animate-bounce" style={{ animationDelay: '0.15s' }} />
                  <div className="w-2 h-2 bg-text-muted rounded-full animate-bounce" style={{ animationDelay: '0.3s' }} />
                </div>
              </div>
            </motion.div>
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
        {!isStreaming && !isLoading && messages.length > 0 && !prdPreview && !isGeneratingPRD && !isGeneratingSummary && (
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

        {/* Match Experts Button */}
        {!isStreaming && !isLoading && messages.length > 0 && !isMatchingExperts && matchedExperts.length === 0 && (
          <div className="px-3 pb-2 bg-white border-t border-border" data-testid="expert-actions">
            <button
              onClick={handleMatchExperts}
              disabled={!canMatchExperts()}
              className={twMerge(
                'w-full py-2 px-3 rounded-md transition-colors flex items-center justify-center gap-2 text-sm font-medium',
                canMatchExperts()
                  ? 'bg-purple-600 hover:bg-purple-700 text-white'
                  : 'bg-gray-200 text-gray-500 cursor-not-allowed'
              )}
              data-testid="match-experts-button"
            >
              <UserPlus className="w-4 h-4" />
              Match Experts
            </button>
            {!canMatchExperts() && (
              <div className="text-[10px] text-gray-500 mt-1 text-center">
                Share your business challenges to find matching experts
              </div>
            )}
          </div>
        )}

        {/* Quick Reply Buttons */}
        {!isStreaming && !isLoading && messages.length > 0 && !prdPreview && !isGeneratingPRD && !isGeneratingSummary && matchedExperts.length === 0 && (
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
