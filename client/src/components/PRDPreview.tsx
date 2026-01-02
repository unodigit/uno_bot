import { motion, AnimatePresence } from 'framer-motion'
import { Download, FileText, X, Maximize2 } from 'lucide-react'
import { useChatStore } from '../stores/chatStore'
import ReactMarkdown from 'react-markdown'
import { useState } from 'react'

interface PRDPreviewProps {
  onDismiss?: () => void
}

export function PRDPreview({ onDismiss }: PRDPreviewProps) {
  const { prdPreview, downloadPRD, clearPRDPreview } = useChatStore()
  const [showFull, setShowFull] = useState(false)

  if (!prdPreview) {
    return null
  }

  const handleDownload = async () => {
    try {
      await downloadPRD(prdPreview.id)
    } catch (error) {
      console.error('Download failed:', error)
    }
  }

  const handleDismiss = () => {
    clearPRDPreview()
    if (onDismiss) {
      onDismiss()
    }
  }

  // Full-screen modal view
  if (showFull) {
    return (
      <AnimatePresence>
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
          onClick={(e) => {
            if (e.target === e.currentTarget) setShowFull(false)
          }}
        >
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.95, opacity: 0 }}
            className="bg-white rounded-lg shadow-2xl w-full max-w-5xl max-h-[90vh] flex flex-col overflow-hidden"
          >
            <div className="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FileText className="w-5 h-5" />
                <span className="font-semibold">{prdPreview.filename}</span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={handleDownload}
                  className="px-3 py-1.5 bg-white/20 hover:bg-white/30 rounded text-sm"
                >
                  Download
                </button>
                <button
                  onClick={() => setShowFull(false)}
                  className="p-2 hover:bg-white/20 rounded"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>
            <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
              <div className="prose prose-blue max-w-none bg-white p-6 rounded-lg border border-gray-200 shadow-sm">
                <ReactMarkdown
                  components={{
                    h1: ({ node, ...props }) => <h1 className="text-3xl font-bold text-gray-900 mb-4 pb-2 border-b-2 border-blue-500" {...props} />,
                    h2: ({ node, ...props }) => <h2 className="text-2xl font-bold text-gray-800 mt-6 mb-3" {...props} />,
                    h3: ({ node, ...props }) => <h3 className="text-xl font-semibold text-gray-700 mt-5 mb-2" {...props} />,
                    h4: ({ node, ...props }) => <h4 className="text-lg font-semibold text-gray-700 mt-4 mb-2" {...props} />,
                    ul: ({ node, ...props }) => <ul className="list-disc list-inside ml-4 space-y-1 my-3" {...props} />,
                    ol: ({ node, ...props }) => <ol className="list-decimal list-inside ml-4 space-y-1 my-3" {...props} />,
                    li: ({ node, ...props }) => <li className="pl-1" {...props} />,
                    p: ({ node, ...props }) => <p className="my-2 leading-relaxed text-gray-700" {...props} />,
                    code: ({ node, ...props }) => <code className="bg-gray-100 px-1.5 py-0.5 rounded text-sm font-mono text-gray-800" {...props} />,
                    pre: ({ node, ...props }) => <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto my-3" {...props} />,
                    blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-600 my-3" {...props} />,
                    a: ({ node, ...props }) => <a className="text-blue-600 hover:text-blue-800 underline" target="_blank" rel="noopener noreferrer" {...props} />,
                  }}
                >
                  {prdPreview.preview_text || "No content available"}
                </ReactMarkdown>
              </div>
            </div>
          </motion.div>
        </motion.div>
      </AnimatePresence>
    )
  }

  // Compact preview card (original view)
  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 10 }}
        className="bg-white border border-border rounded-lg p-4 shadow-sm mb-3"
        data-testid="prd-preview"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <FileText className="w-4 h-4 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-sm text-text">{prdPreview.filename}</h3>
              <p className="text-xs text-text-muted">Project Requirements Document</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-text-muted bg-gray-100 px-2 py-1 rounded">
              v{prdPreview.version}
            </span>
            <button
              onClick={handleDismiss}
              className="w-8 h-8 p-1 hover:bg-gray-100 rounded transition-colors flex items-center justify-center min-w-[36px] min-h-[36px]"
              aria-label="Close PRD preview"
            >
              <X className="w-4 h-4 text-text-muted" />
            </button>
          </div>
        </div>

        {/* Preview Content - Using React Markdown for rendering */}
        <div className="bg-gray-50 rounded-lg p-3 mb-3 max-h-48 overflow-y-auto">
          <div className="text-xs text-text-muted mb-1">Preview</div>
          <div className="text-sm leading-relaxed bg-white p-2 rounded border prose prose-sm max-w-none">
            <ReactMarkdown
              components={{
                p: ({ node, ...props }) => <p className="my-1" {...props} />,
                strong: ({ node, ...props }) => <strong className="font-semibold text-gray-900" {...props} />,
                em: ({ node, ...props }) => <em className="italic text-gray-700" {...props} />,
                ul: ({ node, ...props }) => <ul className="list-disc list-inside ml-2 my-1" {...props} />,
                li: ({ node, ...props }) => <li className="pl-1" {...props} />,
              }}
            >
              {prdPreview.preview_text || "No preview available"}
            </ReactMarkdown>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={handleDownload}
            className="flex items-center gap-2 px-3 py-3 min-h-[44px] bg-primary text-white text-sm rounded-md hover:bg-primary-dark transition-colors flex-1"
            data-testid="download-prd-button"
            aria-label={`Download PRD file ${prdPreview.filename}`}
          >
            <Download className="w-4 h-4" />
            Download
          </button>
          <button
            onClick={() => setShowFull(true)}
            className="flex items-center gap-2 px-3 py-3 min-h-[44px] bg-gray-100 text-text text-sm rounded-md hover:bg-gray-200 transition-colors"
            data-testid="view-full-prd-button"
            aria-label="View full PRD with markdown rendering"
          >
            <Maximize2 className="w-4 h-4" />
            Full View
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
