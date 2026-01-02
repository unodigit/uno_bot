import { useState, useEffect } from 'react'
import { CheckCircle, XCircle, Loader2 } from 'lucide-react'
import { Button } from '../components/ui/Button'

interface UnsubscribePageProps {
  sessionId?: string
}

export function UnsubscribePage({ sessionId: urlSessionId }: UnsubscribePageProps) {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')

  useEffect(() => {
    const unsubscribe = async () => {
      try {
        // Get session ID from URL params if not provided
        const sessionId = urlSessionId || new URLSearchParams(window.location.search).get('session_id')

        if (!sessionId) {
          setStatus('error')
          setMessage('Invalid unsubscribe link. Please contact support.')
          return
        }

        // Call unsubscribe API
        const response = await fetch('/api/v1/sessions/unsubscribe', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: sessionId
          })
        })

        if (response.ok) {
          setStatus('success')
          setMessage('You have been successfully unsubscribed from marketing emails.')
        } else {
          setStatus('error')
          setMessage('Failed to unsubscribe. Please try again or contact support.')
        }
      } catch (error) {
        console.error('Unsubscribe error:', error)
        setStatus('error')
        setMessage('Network error. Please try again later.')
      }
    }

    unsubscribe()
  }, [urlSessionId])

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-6">
        <div className="text-center">
          {status === 'loading' && (
            <>
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100">
                <Loader2 className="h-6 w-6 text-blue-600 animate-spin" />
              </div>
              <h2 className="mt-4 text-lg font-medium text-gray-900">Processing Unsubscribe Request</h2>
              <p className="mt-2 text-sm text-gray-600">Please wait while we process your request...</p>
            </>
          )}

          {status === 'success' && (
            <>
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100">
                <CheckCircle className="h-6 w-6 text-green-600" />
              </div>
              <h2 className="mt-4 text-lg font-medium text-gray-900">Successfully Unsubscribed</h2>
              <p className="mt-2 text-sm text-gray-600">{message}</p>
            </>
          )}

          {status === 'error' && (
            <>
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                <XCircle className="h-6 w-6 text-red-600" />
              </div>
              <h2 className="mt-4 text-lg font-medium text-gray-900">Unsubscribe Failed</h2>
              <p className="mt-2 text-sm text-gray-600">{message}</p>
            </>
          )}
        </div>

        <div className="mt-6">
          <Button
            onClick={() => window.location.href = '/'}
            className="w-full"
          >
            Return to Homepage
          </Button>
        </div>

        <div className="mt-6 text-center text-xs text-gray-500">
          <p>
            If you have any questions or need assistance,
            <br />
            please contact our support team.
          </p>
        </div>
      </div>
    </div>
  )
}