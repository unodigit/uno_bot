import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Shield, CheckCircle, X } from 'lucide-react'
import { twMerge } from 'tailwind-merge'

interface ConsentModalProps {
  isOpen: boolean
  onAccept: () => void
  onDecline: () => void
}

export function ConsentModal({ isOpen, onAccept, onDecline }: ConsentModalProps) {
  const [hasScrolled, setHasScrolled] = useState(false)

  const handleAccept = () => {
    // Store consent in localStorage with timestamp
    const consentData = {
      accepted: true,
      timestamp: new Date().toISOString(),
      version: '1.0'
    }
    localStorage.setItem('uno_consent', JSON.stringify(consentData))
    onAccept()
  }

  const handleDecline = () => {
    // Store decline in localStorage with timestamp
    const consentData = {
      accepted: false,
      timestamp: new Date().toISOString(),
      version: '1.0'
    }
    localStorage.setItem('uno_consent', JSON.stringify(consentData))
    onDecline()
  }

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={handleDecline} // Click outside to decline
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                    <Shield className="w-6 h-6" />
                  </div>
                  <div>
                    <h2 className="text-xl font-bold">Privacy & Data Consent</h2>
                    <p className="text-sm text-blue-100">UnoDigit Business Consultation</p>
                  </div>
                </div>
                <button
                  onClick={handleDecline}
                  className="text-white hover:text-gray-200 transition-colors"
                  aria-label="Close consent modal"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>

            {/* Content */}
            <div className="p-6 space-y-6 max-h-[60vh] overflow-y-auto" onScroll={() => setHasScrolled(true)}>
              <div className="space-y-4">
                <h3 className="text-lg font-semibold text-text">Data Collection & Processing</h3>
                <p className="text-text-muted text-sm leading-relaxed">
                  Before we begin collecting your personal information, we need your consent to process your data
                  in accordance with our privacy policy and applicable data protection regulations including GDPR.
                </p>
              </div>

              <div className="space-y-4">
                <h4 className="font-medium text-text">What data we collect:</h4>
                <ul className="space-y-2 text-sm text-text-muted">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span><strong>Personal Information:</strong> Name, email address, company information</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span><strong>Business Context:</strong> Industry, company size, business challenges</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span><strong>Conversation Data:</strong> Chat messages and interaction history</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span><strong>Technical Data:</strong> Browser information, IP address, session data</span>
                  </li>
                </ul>
              </div>

              <div className="space-y-4">
                <h4 className="font-medium text-text">How we use your data:</h4>
                <ul className="space-y-2 text-sm text-text-muted">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span>Provide personalized AI consultation and business recommendations</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span>Generate Project Requirements Documents (PRDs)</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span>Match you with appropriate UnoDigit experts</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span>Send booking confirmations and appointment reminders</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span>Improve our AI models and service quality</span>
                  </li>
                </ul>
              </div>

              <div className="space-y-4">
                <h4 className="font-medium text-text">Your rights:</h4>
                <ul className="space-y-2 text-sm text-text-muted">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span>Right to access, correct, or delete your personal data</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span>Right to withdraw consent at any time</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span>Right to data portability</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <span>Right to lodge complaints with supervisory authorities</span>
                  </li>
                </ul>
              </div>

              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-800">
                  <strong>Note:</strong> By declining consent, you will not be able to use our consultation services
                  that require personal data collection. However, you may still browse our website and contact us
                  through other channels.
                </p>
              </div>
            </div>

            {/* Footer */}
            <div className="bg-gray-50 p-6 border-t border-gray-200">
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={handleDecline}
                  className="flex-1 py-3 px-4 text-gray-700 bg-white border border-gray-300 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                >
                  Decline
                </button>
                <button
                  onClick={handleAccept}
                  disabled={!hasScrolled}
                  className={twMerge(
                    "flex-1 py-3 px-4 text-white rounded-lg font-medium transition-colors",
                    hasScrolled
                      ? "bg-blue-600 hover:bg-blue-700"
                      : "bg-gray-400 cursor-not-allowed"
                  )}
                >
                  I Agree - Continue
                </button>
              </div>
              <p className="text-xs text-text-muted text-center mt-3">
                You must scroll through this consent form to enable the Accept button
              </p>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}