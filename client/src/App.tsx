import { useEffect } from 'react'
import { ChatWidget } from './components/ChatWidget'
import { useChatStore } from './stores/chatStore'

function App() {
  const { loadSession } = useChatStore()

  // Check for session ID in URL parameters on app load
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const sessionId = urlParams.get('session_id')

    if (sessionId) {
      // Load session if session_id parameter is present in URL
      loadSession(sessionId)
    }
  }, [loadSession])

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-16">
        <h1 className="text-4xl font-bold text-center mb-8">
          Welcome to UnoDigit
        </h1>
        <p className="text-center text-text-muted">
          AI-Powered Business Consulting
        </p>
      </div>
      <ChatWidget />
    </div>
  )
}

export default App
