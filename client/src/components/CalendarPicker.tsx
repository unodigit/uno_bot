import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Calendar, Clock, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react'
import { twMerge } from 'tailwind-merge'

export interface TimeSlot {
  start_time: string
  end_time: string
  timezone: string
  display_time: string
  display_date: string
}

export interface AvailabilityResponse {
  expert_id: string
  expert_name: string
  timezone: string
  slots: TimeSlot[]
  generated_at: string
}

interface CalendarPickerProps {
  expertId: string
  expertName: string
  onSelectSlot: (slot: TimeSlot) => void
  onBack: () => void
}

export function CalendarPicker({ expertId, expertName, onSelectSlot, onBack }: CalendarPickerProps) {
  const [slots, setSlots] = useState<TimeSlot[]>([])
  const [selectedSlot, setSelectedSlot] = useState<TimeSlot | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [timezone, setTimezone] = useState('UTC')

  // Get user's timezone
  useEffect(() => {
    const detectedTz = Intl.DateTimeFormat().resolvedOptions().timeZone
    setTimezone(detectedTz)
  }, [])

  // Fetch availability
  useEffect(() => {
    fetchAvailability()
  }, [expertId])

  const fetchAvailability = async () => {
    try {
      setLoading(true)
      setError(null)

      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(
        `${API_BASE_URL}/api/v1/bookings/experts/${expertId}/availability?timezone=${encodeURIComponent(timezone)}`
      )

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }

      const data: AvailabilityResponse = await response.json()
      setSlots(data.slots)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load availability')
    } finally {
      setLoading(false)
    }
  }

  // Auto-refresh availability every 30 seconds when confirming
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>
    if (selectedSlot) {
      interval = setInterval(() => {
        fetchAvailability()
      }, 30000)
    }
    return () => {
      if (interval) clearInterval(interval)
    }
  }, [selectedSlot, expertId, timezone])

  const handleSlotSelect = (slot: TimeSlot) => {
    setSelectedSlot(slot)
  }

  const handleConfirm = () => {
    if (selectedSlot) {
      onSelectSlot(selectedSlot)
    }
  }

  // Group slots by date
  const slotsByDate = slots.reduce((acc, slot) => {
    const date = slot.display_date
    if (!acc[date]) acc[date] = []
    acc[date].push(slot)
    return acc
  }, {} as Record<string, TimeSlot[]>)

  // Get unique dates and sort them
  const dates = Object.keys(slotsByDate).sort()

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
            className="text-xs text-text-muted hover:text-text px-2 py-1 rounded hover:bg-surface"
            aria-label="Back to booking confirmation"
          >
            ← Back
          </button>
          <h3 className="text-sm font-semibold text-text">Select Time Slot</h3>
        </div>
        <div className="text-xs text-text-muted flex items-center gap-1">
          <Clock className="w-3 h-3" />
          {timezone}
        </div>
      </div>

      {/* Expert Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-xs">
            {expertName.charAt(0).toUpperCase()}
          </div>
          <div>
            <div className="text-sm font-semibold text-text">{expertName}</div>
            <div className="text-xs text-text-muted">Available for consultation</div>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="flex flex-col items-center justify-center py-8 gap-2">
          <Loader2 className="w-6 h-6 text-primary animate-spin" />
          <p className="text-sm text-text-muted">Loading available slots...</p>
        </div>
      )}

      {/* Error State */}
      {error && !loading && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-3">
          <div className="flex items-start gap-2">
            <AlertCircle className="w-4 h-4 text-red-600 mt-0.5" />
            <div className="flex-1">
              <p className="text-sm text-text">Failed to load availability</p>
              <p className="text-xs text-red-600 mt-1">{error}</p>
              <p className="text-xs text-error underline mt-2 hover:text-error-dark">
                Try again
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Slots List */}
      {!loading && !error && (
        <>
          {dates.length === 0 ? (
            <div className="text-center py-8">
              <Calendar className="w-12 h-12 text-gray-300 mx-auto mb-2" />
              <p className="text-sm text-text-muted">No available slots found</p>
              <p className="text-xs text-text-muted mt-1">Try checking back later</p>
            </div>
          ) : (
            <div className="space-y-4 max-h-[320px] overflow-y-auto pr-2">
              {dates.map((date) => (
                <div key={date} className="space-y-2">
                  <div className="text-xs font-semibold text-text bg-surface px-2 py-1 rounded border border-border">
                    {formatDateDisplay(date)}
                  </div>
                  <div className="grid grid-cols-2 gap-2">
                    {slotsByDate[date].map((slot, idx) => {
                      const isSelected = selectedSlot?.start_time === slot.start_time
                      return (
                        <motion.button
                          key={slot.start_time}
                          initial={{ opacity: 0, y: 10 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: idx * 0.05 }}
                          onClick={() => handleSlotSelect(slot)}
                          className={twMerge(
                            'px-3 py-2 rounded-lg border text-sm font-medium transition-all',
                            isSelected
                              ? 'bg-primary border-primary text-white shadow-md'
                              : 'bg-white border-border text-text hover:border-primary hover:bg-surface'
                          )}
                          aria-label={`Select ${slot.display_time} on ${formatDateDisplay(slot.display_date)} in ${slot.timezone}`}
                          aria-pressed={isSelected}
                        >
                          {slot.display_time}
                        </motion.button>
                      )
                    })}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Confirm Button */}
          <AnimatePresence>
            {selectedSlot && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-4 pt-4 border-t border-gray-200"
              >
                <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-3">
                  <div className="flex items-center gap-2 text-green-800 text-sm">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Selected: <strong>{formatDateDisplay(selectedSlot.display_date)} at {selectedSlot.display_time}</strong></span>
                  </div>
                </div>
                <button
                  onClick={handleConfirm}
                  className="w-full py-2 bg-primary hover:bg-primary-dark text-white rounded-lg font-medium transition-colors"
                  aria-label="Confirm booking with selected time slot"
                >
                  Confirm Booking
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </>
      )}
    </motion.div>
  )
}

function formatDateDisplay(dateStr: string): string {
  const date = new Date(dateStr + 'T00:00:00') // Ensure local timezone
  const today = new Date()
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)

  const dateOnly = date.toISOString().split('T')[0]
  const todayOnly = today.toISOString().split('T')[0]
  const tomorrowOnly = tomorrow.toISOString().split('T')[0]

  if (dateOnly === todayOnly) return 'Today'
  if (dateOnly === tomorrowOnly) return 'Tomorrow'

  return date.toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  })
}
