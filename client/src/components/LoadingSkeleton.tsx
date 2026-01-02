import { twMerge } from 'tailwind-merge'

interface SkeletonProps {
  className?: string
  width?: string
  height?: string
  variant?: 'text' | 'circle' | 'rectangle'
}

/**
 * LoadingSkeleton Component
 * Consistent loading skeleton for better UX during data fetching
 */
export function LoadingSkeleton({ className = '', width, height, variant = 'text' }: SkeletonProps) {
  const baseClasses = 'animate-pulse bg-gray-200 rounded'

  const variantClasses = {
    text: 'h-4 w-full',
    circle: 'rounded-full',
    rectangle: 'w-full h-full',
  }

  const sizeStyle = {
    width: width || (variant === 'circle' ? '1rem' : '100%'),
    height: height || (variant === 'circle' ? '1rem' : '1rem'),
  }

  return (
    <div
      className={twMerge(baseClasses, variantClasses[variant], className)}
      style={sizeStyle}
      aria-hidden="true"
    />
  )
}

/**
 * CardSkeleton Component
 * Skeleton for card components
 */
export function CardSkeleton({ className = '' }: { className?: string }) {
  return (
    <div className={twMerge('bg-white rounded-lg p-4 border border-gray-200', className)}>
      <div className="flex gap-3">
        <LoadingSkeleton variant="circle" width="3rem" height="3rem" />
        <div className="flex-1 space-y-2">
          <LoadingSkeleton variant="text" />
          <LoadingSkeleton variant="text" width="60%" />
        </div>
      </div>
      <div className="mt-3 space-y-2">
        <LoadingSkeleton variant="text" />
        <LoadingSkeleton variant="text" width="80%" />
      </div>
    </div>
  )
}

/**
 * ListSkeleton Component
 * Skeleton for list items
 */
export function ListSkeleton({ count = 3, className = '' }: { count?: number; className?: string }) {
  return (
    <div className={twMerge('space-y-3', className)}>
      {Array.from({ length: count }).map((_, i) => (
        <CardSkeleton key={i} />
      ))}
    </div>
  )
}

/**
 * PageSkeleton Component
 * Full page loading skeleton
 */
export function PageSkeleton() {
  return (
    <div className="space-y-6 p-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="space-y-2">
        <LoadingSkeleton variant="text" height="2rem" width="50%" />
        <LoadingSkeleton variant="text" width="30%" />
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <LoadingSkeleton variant="rectangle" height="4rem" />
        <LoadingSkeleton variant="rectangle" height="4rem" />
        <LoadingSkeleton variant="rectangle" height="4rem" />
      </div>

      {/* Content */}
      <ListSkeleton count={4} />
    </div>
  )
}
