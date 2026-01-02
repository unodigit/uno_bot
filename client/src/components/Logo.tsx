import { twMerge } from 'tailwind-merge'

interface LogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
  variant?: 'full' | 'icon' | 'text'
}

/**
 * UnoDigit Logo Component
 * Displays the UnoDigit logo with consistent sizing and styling
 */
export function Logo({ size = 'md', className = '', variant = 'full' }: LogoProps) {
  const sizeClasses = {
    sm: 'w-6 h-6 text-xs',
    md: 'w-8 h-8 text-sm',
    lg: 'w-12 h-12 text-base',
    xl: 'w-16 h-16 text-lg',
  }

  const baseClasses = 'flex items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-indigo-700 text-white font-bold'

  if (variant === 'icon' || variant === 'full') {
    return (
      <div className={twMerge(baseClasses, sizeClasses[size], className)}>
        <span className="font-bold">UD</span>
      </div>
    )
  }

  // Full logo with text
  return (
    <div className={twMerge('flex items-center gap-2', className)}>
      <div className={twMerge(baseClasses, sizeClasses[size])}>
        <span className="font-bold">UD</span>
      </div>
      <span className="font-semibold text-text">UnoDigit</span>
    </div>
  )
}

/**
 * Avatar Component
 * Displays user/expert avatar with fallback
 */
interface AvatarProps {
  src?: string | null
  name: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  className?: string
}

export function Avatar({ src, name, size = 'md', className = '' }: AvatarProps) {
  const sizeClasses = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-12 h-12 text-sm',
    lg: 'w-16 h-16 text-base',
    xl: 'w-24 h-24 text-lg',
  }

  if (src) {
    return (
      <img
        src={src}
        alt={name}
        className={twMerge('rounded-full object-cover border-2 border-white shadow-sm', sizeClasses[size], className)}
      />
    )
  }

  // Fallback to initials
  const initials = name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)

  return (
    <div className={twMerge(
      'rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 text-white flex items-center justify-center font-semibold',
      sizeClasses[size],
      className
    )}>
      {initials}
    </div>
  )
}
