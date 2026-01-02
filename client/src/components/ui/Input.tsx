import React from 'react'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  className?: string
}

export function Input({ className = '', ...props }: InputProps) {
  const baseClasses = 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent'

  return (
    <input className={`${baseClasses} ${className}`} {...props} />
  )
}