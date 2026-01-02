import { ChatWidget } from './components/ChatWidget'

function App() {
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
