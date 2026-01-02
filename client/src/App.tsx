import { useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { ChatWidget } from './components/ChatWidget'
import { useChatStore } from './stores/chatStore'
import AdminPage from './pages/AdminPage'
import { DialogDemo } from './pages/DialogDemo'
import ErrorBoundary from './components/ErrorBoundary'

function Home() {
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

function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="/dialog-demo" element={<DialogDemo />} />
        </Routes>
      </BrowserRouter>
    </ErrorBoundary>
  )
}

export default App
