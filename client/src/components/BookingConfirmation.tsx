import { motion, AnimatePresence } from 'framer-motion'
import { Calendar, Clock, User, Mail, Link as LinkIcon, CheckCircle2, ExternalLink } from 'lucide-react'
import { TimeSlot } from './CalendarPicker'

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
}

export function BookingConfirmation({ booking, onDone }: BookingConfirmationProps) {
  const startTime = new Date(booking.start_time)
  const endTime = new Date(booking.end_time)

  const formatDateTime = (date: Date) => {
    return date.toLocaleString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      timeZone: booking.timezone
    })
  }

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
    >
      {/* Success Header */}
      <div className="text-center mb-4">
        <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
          <CheckCircle2 className="w-6 h-6 text-green-600" />
        </div>
        <h3 className="text-lg font-bold text-gray-900">Booking Confirmed!</h3>
        <p className="text-sm text-gray-600 mt-1">Your appointment has been scheduled</p>
      </div>

      {/* Booking Details Card */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4 mb-4">
        {/* Expert Info */}
        <div className="flex items-start gap-3 mb-4 pb-4 border-b border-blue-200/50">
          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
            {booking.expert_name.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <div className="font-semibold text-gray-900">{booking.expert_name}</div>
            <div className="text-xs text-gray-600">{booking.expert_role}</div>
          </div>
        </div>

        {/* Date & Time */}
        <div className="space-y-2 mb-4 pb-4 border-b border-blue-200/50">
          <div className="flex items-start gap-2">
            <Calendar className="w-4 h-4 text-blue-600 mt-0.5" />
            <div className="flex-1">
              <div className="text-sm font-medium text-gray-900">
                {startTime.toLocaleDateString('en-US', {
                  weekday: 'long',
                  month: 'long',
                  day: 'numeric',
                  year: 'numeric'
                })}
              </div>
              <div className="text-xs text-gray-600">
                {formatTime(startTime)} - {formatTime(endTime)} ({booking.timezone})
              </div>
            </div>
          </div>
        </div>

        {/* Attendees */}
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-sm">
            <User className="w-4 h-4 text-gray-500" />
            <span className="font-medium text-gray-900">{booking.client_name}</span>
          </div>
          <div className="flex items-center gap-2 text-sm">
            <Mail className="w-4 h-4 text-gray-500" />
            <span className="text-gray-700">{booking.client_email}</span>
          </div>
        </div>
      </div>

      {/* Meeting Link */}
      {booking.meeting_link && (
        <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
          <div className="flex items-center gap-2 mb-2">
            <LinkIcon className="w-4 h-4 text-primary" />
            <span className="font-semibold text-sm text-gray-900">Meeting Link</span>
          </div>
          <a
            href={booking.meeting_link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 text-sm text-primary hover:text-primary-dark underline break-all"
          >
            {booking.meeting_link}
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      )}

      {/* What's Next */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-4">
        <h4 className="font-semibold text-sm text-gray-900 mb-2">What's Next?</h4>
        <ul className="text-xs text-gray-600 space-y-1 list-disc list-inside">
          <li>A calendar invite has been sent to your email</li>
          <li>You'll receive a reminder 24 hours before</li>
          <li>Join the meeting using the link above</li>
        </ul>
      </div>

      {/* Done Button */}
      <button
        onClick={onDone}
        className="w-full py-2 bg-primary hover:bg-primary-dark text-white rounded-lg font-medium transition-colors"
      >
        Done
      </button>
    </motion.div>
  )
}
