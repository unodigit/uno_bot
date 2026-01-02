import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, CheckCircle, AlertCircle, Info } from 'lucide-react'
import { twMerge } from 'tailwind-merge'

export type ToastType = 'success' | 'error' | 'info' | 'warning'

export interface ToastProps {
  id: string
  message: string
  type?: ToastType
  duration?: number
  onClose?: (id: string) => void
}

export function Toast({ id, message, type = 'info', duration = 5000, onClose }: ToastProps) {
  useEffect(() => {
    if (onClose) {
      const timer = setTimeout(() => onClose(id), duration)
      return () => clearTimeout(timer)
    }
  }, [id, duration, onClose])

  const getIcon = () => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-success" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-error" />
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-warning" />
      default:
        return <Info className="w-5 h-5 text-primary" />
    }
  }

  const getContainerClasses = () => {
    switch (type) {
      case 'success':
        return 'border-success/20 bg-success/5'
      case 'error':
        return 'border-error/20 bg-error/5'
      case 'warning':
        return 'border-warning/20 bg-warning/5'
      default:
        return 'border-primary/20 bg-primary/5'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: 20, scale: 0.95 }}
      transition={{ type: 'spring', stiffness: 300, damping: 25 }}
      className={twMerge(
        'toast',
        getContainerClasses()
      )}
      role="alert"
      aria-live="polite"
    >
      <div className="flex items-start gap-3 flex-1">
        <div className="mt-0.5">{getIcon()}</div>
        <div className="flex-1 text-sm font-medium text-text">{message}</div>
        {onClose && (
          <button
            onClick={() => onClose(id)}
            className="p-1 hover:bg-black/5 rounded transition-colors"
            aria-label="Close notification"
          >
            <X className="w-4 h-4 text-text-muted" />
          </button>
        )}
      </div>
    </motion.div>
  )
}

export interface ToastContainerProps {
  toasts: ToastProps[]
  onDismiss: (id: string) => void
}

export function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-md">
      <AnimatePresence mode="popLayout">
        {toasts.map((toast) => (
          <Toast key={toast.id} {...toast} onClose={onDismiss} />
        ))}
      </AnimatePresence>
    </div>
  )
}

// Internal toast type for state (onClose is added by container)
interface InternalToast {
  id: string
  message: string
  type: ToastType
  duration: number
}

// Hook for showing toasts
export function useToast() {
  const [toasts, setToasts] = useState<InternalToast[]>([])

  const showToast = (message: string, type: ToastType = 'info', duration = 5000) => {
    const id = `toast-${Date.now()}-${Math.random()}`
    setToasts((prev) => [...prev, { id, message, type, duration }])
  }

  const dismissToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }

  // Convert internal toasts to ToastProps for rendering
  const toastProps: ToastProps[] = toasts.map(t => ({
    ...t,
    onClose: dismissToast
  }))

  return { toasts: toastProps, showToast, dismissToast }
}
