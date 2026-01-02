import { TextareaHTMLAttributes } from 'react'
import { twMerge } from 'tailwind-merge'

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  className?: string
  error?: boolean
  errorText?: string
  errorId?: string
}

export function Textarea({ className, error = false, errorText, errorId, disabled, ...props }: TextareaProps) {
  const baseClasses = 'w-full px-3 py-2 min-h-[44px] border rounded-md focus:outline-none focus:ring-2 focus:border-transparent resize-vertical transition-all'

  const stateClasses = error
    ? 'border-error focus:ring-error'
    : 'border-border focus:ring-primary'

  const disabledClasses = disabled
    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
    : ''

  return (
    <div>
      <textarea
        className={twMerge(baseClasses, stateClasses, disabledClasses, className)}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error && errorId ? errorId : undefined}
        disabled={disabled}
        {...props}
      />
      {errorText && error && (
        <p id={errorId} className="mt-1 text-xs text-error flex items-center gap-1">
          <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          {errorText}
        </p>
      )}
    </div>
  )
}