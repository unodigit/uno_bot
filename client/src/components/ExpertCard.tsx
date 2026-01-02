import { motion, AnimatePresence } from 'framer-motion'
import { User, Mail, Award, Star, Briefcase, Calendar, Edit, Trash2 } from 'lucide-react'
import { MatchedExpert, Expert } from '../types'

interface ExpertCardProps {
  expert: MatchedExpert | Expert
  index?: number
  onSelect?: (expert: MatchedExpert) => void
  onBook?: (expert: MatchedExpert) => void
  onEdit?: (expert: Expert) => void
  onDelete?: (expertId: string) => void
  showActions?: boolean
  showAdminActions?: boolean
}

export function ExpertCard({ expert, index = 0, onSelect, onBook, onEdit, onDelete, showActions = true, showAdminActions = false }: ExpertCardProps) {
  const isMatchedExpert = 'match_score' in expert
  const scorePercentage = isMatchedExpert ? Math.round((expert as MatchedExpert).match_score) : null

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm hover:shadow-md transition-shadow relative group"
      data-testid={`expert-card-${index}`}
    >
      <div className="flex items-start gap-3">
        {/* Photo/Avatar */}
        <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center flex-shrink-0 text-white font-bold">
          {expert.photo_url ? (
            <img src={expert.photo_url} alt={expert.name} className="w-12 h-12 rounded-full object-cover" />
          ) : (
            expert.name.charAt(0).toUpperCase()
          )}
        </div>

        {/* Expert Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h4 className="font-semibold text-gray-900 text-sm">{expert.name}</h4>
              <p className="text-xs text-gray-600">{expert.role}</p>
            </div>

            {/* Match Score Badge - only show for matched experts */}
            {isMatchedExpert && scorePercentage !== null && (
              <div className="flex items-center gap-1 bg-blue-50 text-blue-700 px-2 py-1 rounded-full text-xs font-medium">
                <Star className="w-3 h-3 fill-current" />
                {scorePercentage}%
              </div>
            )}
          </div>

          {/* Bio */}
          {expert.bio && (
            <p className="text-xs text-gray-600 mt-1 line-clamp-2">{expert.bio}</p>
          )}

          {/* Email */}
          <div className="flex items-center gap-1 text-xs text-gray-500 mt-1">
            <Mail className="w-3 h-3" />
            {expert.email}
          </div>

          {/* Specialties */}
          {expert.specialties && expert.specialties.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {expert.specialties.slice(0, 3).map((specialty, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 bg-gray-100 text-gray-700 text-[10px] rounded-full border border-gray-200"
                >
                  {specialty}
                </span>
              ))}
              {expert.specialties.length > 3 && (
                <span className="px-2 py-0.5 bg-gray-50 text-gray-500 text-[10px] rounded-full">
                  +{expert.specialties.length - 3}
                </span>
              )}
            </div>
          )}

          {/* Services */}
          {expert.services && expert.services.length > 0 && (
            <div className="flex items-center gap-1 mt-2 text-[10px] text-gray-500">
              <Briefcase className="w-3 h-3" />
              <span className="line-clamp-1">{expert.services.join(', ')}</span>
            </div>
          )}

          {/* Action Buttons - only show if callbacks provided */}
          {showActions && (onSelect || onBook) && (
            <div className="flex gap-2 mt-3">
              {onBook && (
                <button
                  onClick={() => onBook(expert as MatchedExpert)}
                  className="flex-1 px-3 py-1.5 bg-primary hover:bg-primary-dark text-white text-xs rounded transition-colors flex items-center justify-center gap-1"
                  data-testid={`book-expert-${index}`}
                >
                  <Calendar className="w-3 h-3" />
                  Book
                </button>
              )}
              {onSelect && (
                <button
                  onClick={() => onSelect(expert as MatchedExpert)}
                  className="px-3 py-1.5 border border-gray-300 text-gray-700 text-xs rounded hover:bg-gray-50 transition-colors"
                  data-testid={`select-expert-${index}`}
                >
                  Select
                </button>
              )}
              <a
                href={`mailto:${expert.email}?subject=Consultation Request`}
                className="px-3 py-1.5 border border-gray-300 text-gray-700 text-xs rounded hover:bg-gray-50 transition-colors"
                data-testid={`contact-expert-${index}`}
              >
                Contact
              </a>
            </div>
          )}
        </div>

        {/* Admin Action Buttons - Edit/Delete (visible on hover) */}
        {showAdminActions && (onEdit || onDelete) && (
          <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
            {onEdit && (
              <button
                onClick={() => onEdit(expert as Expert)}
                className="p-1.5 bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors"
                data-testid={`edit-expert-${index}`}
                title="Edit"
              >
                <Edit className="w-3 h-3" />
                <span className="sr-only">Edit</span>
              </button>
            )}
            {onDelete && (
              <button
                onClick={() => onDelete(expert.id)}
                className="p-1.5 bg-white border border-red-300 text-red-600 rounded hover:bg-red-50 transition-colors"
                data-testid={`delete-expert-${index}`}
                title="Delete"
              >
                <Trash2 className="w-3 h-3" />
                <span className="sr-only">Delete</span>
              </button>
            )}
          </div>
        )}
      </div>
    </motion.div>
  )
}

interface ExpertMatchListProps {
  experts: MatchedExpert[]
  onSelect?: (expert: MatchedExpert) => void
  onBook?: (expert: MatchedExpert) => void
  showActions?: boolean
  title?: string
}

export function ExpertMatchList({ experts, onSelect, onBook, showActions = true, title = 'Recommended Experts' }: ExpertMatchListProps) {
  if (experts.length === 0) {
    return null
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: 1, height: 'auto' }}
        exit={{ opacity: 0, height: 0 }}
        className="space-y-3"
        data-testid="expert-match-list"
      >
        <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
          <Award className="w-4 h-4 text-primary" />
          {title}
        </h3>
        <div className="space-y-2">
          {experts.map((expert, index) => (
            <ExpertCard
              key={expert.id}
              expert={expert}
              index={index}
              onSelect={onSelect}
              onBook={onBook}
              showActions={showActions}
            />
          ))}
        </div>
      </motion.div>
    </AnimatePresence>
  )
}
