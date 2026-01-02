import { motion, AnimatePresence } from 'framer-motion'
import { Download, FileText, Eye, X } from 'lucide-react'
import { useChatStore } from '../stores/chatStore'

interface PRDPreviewProps {
  onDismiss?: () => void
}

export function PRDPreview({ onDismiss }: PRDPreviewProps) {
  const { prdPreview, downloadPRD, clearPRDPreview } = useChatStore()

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
              className="p-1 hover:bg-gray-100 rounded transition-colors"
              aria-label="Close PRD preview"
            >
              <X className="w-4 h-4 text-text-muted" />
            </button>
          </div>
        </div>

        {/* Preview Content */}
        <div className="bg-gray-50 rounded-lg p-3 mb-3">
          <div className="text-xs text-text-muted mb-1">Preview</div>
          <div className="text-sm leading-relaxed bg-white p-2 rounded border">
            {prdPreview.preview_text}
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={handleDownload}
            className="flex items-center gap-2 px-3 py-2 bg-primary text-white text-sm rounded-md hover:bg-primary-dark transition-colors flex-1"
            data-testid="download-prd-button"
          >
            <Download className="w-4 h-4" />
            Download PRD (.md)
          </button>
          <button
            onClick={() => window.open(`/prd/${prdPreview.id}/preview`, '_blank')}
            className="flex items-center gap-2 px-3 py-2 bg-gray-100 text-text text-sm rounded-md hover:bg-gray-200 transition-colors"
            data-testid="view-full-prd-button"
          >
            <Eye className="w-4 h-4" />
            View Full
          </button>
        </div>
      </motion.div>
    </AnimatePresence>
  )
}