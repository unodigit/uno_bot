import { motion } from 'framer-motion'
import { Calendar, User, Mail, Link as LinkIcon, CheckCircle2, ExternalLink, X } from 'lucide-react'

export interface BookingData {
  id: string
  expert_name: string
  expert_role: string
  start_time: string
  end_time: string
  timezone: string
  meeting_link: string | null
  client_name: string
  client_email: string
}

interface BookingConfirmationProps {
  booking: BookingData
  onDone: () => void
  onCancel: () => void
  isCancelling: boolean
}

export function BookingConfirmation({ booking, onDone, onCancel, isCancelling }: BookingConfirmationProps) {
  const startTime = new Date(booking.start_time)
  const endTime = new Date(booking.end_time)

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      timeZone: booking.timezone
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="w-full"
      data-testid="booking-confirmation-card"
    >
      {/* Success Header */}
      <div className="text-center mb-lg">
        <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-sm" data-testid="success-checkmark">
          <CheckCircle2 className="w-6 h-6 text-secondary" />
        </div>
        <h3 className="text-lg font-bold text-text">Booking Confirmed!</h3>
        <p className="text-sm text-text-muted mt-xs">Your appointment has been scheduled</p>
      </div>

      {/* Booking Details Card */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4 mb-4" data-testid="booking-details-card">
        {/* Expert Info */}
        <div className="flex items-start gap-3 mb-4 pb-4 border-b border-blue-200/50" data-testid="expert-info">
          <div className="w-10 h-10 bg-primary rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0" data-testid="expert-avatar">
            {booking.expert_name.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <div className="font-semibold text-text" data-testid="expert-name">{booking.expert_name}</div>
            <div className="text-xs text-text-muted" data-testid="expert-role">{booking.expert_role}</div>
          </div>
        </div>

        {/* Date & Time */}
        <div className="space-y-2 mb-4 pb-4 border-b border-blue-200/50" data-testid="date-time-section">
          <div className="flex items-start gap-2">
            <Calendar className="w-4 h-4 text-primary mt-0.5" />
            <div className="flex-1">
              <div className="text-sm font-medium text-text" data-testid="booking-date">
                {startTime.toLocaleDateString('en-US', {
                  weekday: 'long',
                  month: 'long',
                  day: 'numeric',
                  year: 'numeric'
                })}
              </div>
              <div className="text-xs text-text-muted" data-testid="booking-time">
                {formatTime(startTime)} - {formatTime(endTime)} ({booking.timezone})
              </div>
            </div>
          </div>
        </div>

        {/* Attendees */}
        <div className="space-y-2" data-testid="attendees-section">
          <div className="flex items-center gap-2 text-sm">
            <User className="w-4 h-4 text-text-muted" />
            <span className="font-medium text-text" data-testid="client-name">{booking.client_name}</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Mail className="w-4 h-4 text-text-muted" />
            <span className="text-text" data-testid="client-email">{booking.client_email}</span>
          </div>
        </div>
      </div>

      {/* Meeting Link */}
      {booking.meeting_link && (
        <div className="bg-white border border-border rounded-lg p-4 mb-4" data-testid="meeting-link-section">
          <div className="flex items-center gap-2 mb-2">
            <LinkIcon className="w-4 h-4 text-primary" />
            <span className="font-semibold text-sm text-text">Meeting Link</span>
          </div>
          <a
            href={booking.meeting_link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-primary hover:text-primary-dark underline break-all"
            data-testid="meeting-link"
            aria-label="Open meeting link in new tab"
          >
            {booking.meeting_link}
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      )}

      {/* What's Next */}
      <div className="bg-surface border border-border rounded-lg p-4 mb-4" data-testid="whats-next-section">
        <h4 className="font-semibold text-sm text-text mb-2">What's Next?</h4>
        <ul className="text-xs text-text-muted space-y-1 list-disc list-inside">
          <li>A calendar invite has been sent to your email</li>
          <li>You'll receive a reminder 24 hours before</li>
          <li>Join the meeting using the link above</li>
        </ul>
      </div>

      {/* Action Buttons */}
      <div className="space-y-2">
        <button
          onClick={onDone}
          className="w-full py-3 min-h-[44px] bg-primary hover:bg-primary-dark text-white rounded-lg font-medium transition-colors shadow-sm hover:shadow"
          data-testid="done-button"
          aria-label="Done viewing booking confirmation"
        >
          Done
        </button>

        <button
          onClick={onCancel}
          disabled={isCancelling}
          className="w-full py-3 min-h-[44px] bg-white border border-red-300 text-error hover:bg-red-50 rounded-lg font-medium transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          data-testid="cancel-button"
          aria-label="Cancel this booking"
        >
          {isCancelling ? (
            <>
              <span className="w-4 h-4 border-2 border-error border-t-transparent rounded-full animate-spin"></span>
              Cancelling...
            </>
          ) : (
            <>
              <X className="w-4 h-4" />
              Cancel Booking
            </>
          )}
        </button>
      </div>
    </motion.div>
  )
}
