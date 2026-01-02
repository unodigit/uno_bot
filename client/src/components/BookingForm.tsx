import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { User, Mail, Calendar, Clock, Loader2, AlertCircle } from 'lucide-react'
import { TimeSlot } from './CalendarPicker'
import { MatchedExpert } from '../types'

interface BookingFormProps {
  expert: MatchedExpert
  timeSlot: TimeSlot
  onBack: () => void
  onSubmit: (name: string, email: string) => Promise<void>
  isSubmitting: boolean
  error: string | null
}

export function BookingForm({ expert, timeSlot, onBack, onSubmit, isSubmitting, error }: BookingFormProps) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [nameTouched, setNameTouched] = useState(false)
  const [emailTouched, setEmailTouched] = useState(false)

  // Load saved info from session storage
  useEffect(() => {
    const savedName = sessionStorage.getItem('booking_name')
    const savedEmail = sessionStorage.getItem('booking_email')
    if (savedName) setName(savedName)
    if (savedEmail) setEmail(savedEmail)
  }, [])

  const isValid = name.trim().length > 0 && email.trim().length > 0 && email.includes('@')

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setName(e.target.value)
    sessionStorage.setItem('booking_name', e.target.value)
  }

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value)
    sessionStorage.setItem('booking_email', e.target.value)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setNameTouched(true)
    setEmailTouched(true)
    if (isValid) {
      await onSubmit(name.trim(), email.trim())
    }
  }

  const startTime = new Date(timeSlot.start_time)
  const endTime = new Date(timeSlot.end_time)

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="w-full"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <button
            onClick={onBack}
            className="text-xs text-gray-600 hover:text-gray-900 px-2 py-2 min-h-[40px] rounded hover:bg-gray-100"
            disabled={isSubmitting}
            aria-label="Back to select time slot"
          >
            ← Back
          </button>
          <h3 className="text-sm font-semibold text-gray-900">Confirm Booking</h3>
        </div>
      </div>

      {/* Selected Slot Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
            {expert.name.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <div className="font-semibold text-gray-900 text-sm">{expert.name}</div>
            <div className="text-xs text-gray-600">{expert.role}</div>
            <div className="mt-2 flex items-center gap-2 text-xs text-blue-800">
              <Calendar className="w-3 h-3" />
              {startTime.toLocaleDateString('en-US', {
                weekday: 'short',
                month: 'short',
                day: 'numeric'
              })}
            </div>
            <div className="flex items-center gap-2 text-xs text-blue-800 mt-1">
              <Clock className="w-3 h-3" />
              {startTime.toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit'
              })} - {endTime.toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit'
              })}
            </div>
          </div>
        </div>
      </div>

      {/* Error Banner */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-4"
            aria-live="polite"
          >
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
              <AlertCircle className="w-4 h-4 text-red-600 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-red-800">{error}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-3">
        {/* Name Field */}
        <div>
          <label htmlFor="name" className="block text-xs font-medium text-gray-700 mb-1">
            Your Name
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <User className="w-4 h-4 text-gray-400" />
            </div>
            <input
              id="name"
              type="text"
              value={name}
              onChange={handleNameChange}
              onBlur={() => setNameTouched(true)}
              placeholder="John Doe"
              className={twMerge(
                'w-full pl-9 pr-3 py-2 min-h-[44px] border rounded-md text-sm focus:outline-none focus:ring-2 transition-colors',
                nameTouched && name.trim().length === 0
                  ? 'border-red-300 focus:border-red-500 focus:ring-red-200'
                  : 'border-gray-300 focus:border-primary focus:ring-primary/20'
              )}
              disabled={isSubmitting}
              aria-describedby={nameTouched && name.trim().length === 0 ? 'name-error' : undefined}
              aria-invalid={nameTouched && name.trim().length === 0 ? 'true' : 'false'}
            />
          </div>
          {nameTouched && name.trim().length === 0 && (
            <p id="name-error" className="text-xs text-red-600 mt-1">Name is required</p>
          )}
        </div>

        {/* Email Field */}
        <div>
          <label htmlFor="email" className="block text-xs font-medium text-gray-700 mb-1">
            Email Address
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Mail className="w-4 h-4 text-gray-400" />
            </div>
            <input
              id="email"
              type="email"
              value={email}
              onChange={handleEmailChange}
              onBlur={() => setEmailTouched(true)}
              placeholder="john@example.com"
              className={twMerge(
                'w-full pl-9 pr-3 py-2 min-h-[44px] border rounded-md text-sm focus:outline-none focus:ring-2 transition-colors',
                emailTouched && !email.includes('@')
                  ? 'border-red-300 focus:border-red-500 focus:ring-red-200'
                  : 'border-gray-300 focus:border-primary focus:ring-primary/20'
              )}
              disabled={isSubmitting}
              aria-describedby={emailTouched && !email.includes('@') ? 'email-error' : undefined}
              aria-invalid={emailTouched && !email.includes('@') ? 'true' : 'false'}
            />
          </div>
          {emailTouched && !email.includes('@') && (
            <p id="email-error" className="text-xs text-red-600 mt-1">Valid email is required</p>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={!isValid || isSubmitting}
          className={twMerge(
            'w-full py-3 min-h-[44px] rounded-lg font-medium transition-colors flex items-center justify-center gap-2',
            isValid && !isSubmitting
              ? 'bg-primary hover:bg-primary-dark text-white'
              : 'bg-gray-200 text-gray-500 cursor-not-allowed'
          )}
        >
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Calendar className="w-4 h-4" />
              Confirm Booking
            </>
          )}
        </button>

        {/* Privacy Notice */}
        <p className="text-[10px] text-gray-500 text-center mt-2">
          By confirming, you agree to share your contact information with {expert.name} for this appointment.
        </p>
      </form>
    </motion.div>
  )
}

function twMerge(...classes: (string | boolean | undefined | null)[]): string {
  return classes.filter(Boolean).join(' ')
}
