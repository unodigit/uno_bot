import { useState } from 'react'
import { Edit, Save, X } from 'lucide-react'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Textarea } from './ui/Textarea'

interface EditExpertFormProps {
  expert: any
  onSave: (updatedExpert: any) => void
  onCancel: () => void
  isSaving: boolean
}

export function EditExpertForm({ expert, onSave, onCancel, isSaving }: EditExpertFormProps) {
  const [formData, setFormData] = useState({
    name: expert.name || '',
    email: expert.email || '',
    role: expert.role || '',
    bio: expert.bio || '',
    photo_url: expert.photo_url || '',
    specialties: (expert.specialties || []).join(', '),
    services: (expert.services || []).join(', '),
    is_active: expert.is_active || false,
  })

  const handleChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    // Process arrays
    const updatedExpert = {
      ...formData,
      specialties: formData.specialties.split(',').map(s => s.trim()).filter(s => s),
      services: formData.services.split(',').map(s => s.trim()).filter(s => s),
    }

    onSave(updatedExpert)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
        <div className="flex items-center justify-between p-4 border-b">
          <h2 className="text-lg font-semibold">Edit Expert</h2>
          <button
            onClick={onCancel}
            className="p-1 hover:bg-gray-100 rounded transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Name
            </label>
            <Input
              value={formData.name}
              onChange={(e) => handleChange('name', e.target.value)}
              placeholder="Expert name"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <Input
              type="email"
              value={formData.email}
              onChange={(e) => handleChange('email', e.target.value)}
              placeholder="expert@example.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Role
            </label>
            <Input
              value={formData.role}
              onChange={(e) => handleChange('role', e.target.value)}
              placeholder="e.g., Senior Developer, AI Consultant"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Bio
            </label>
            <Textarea
              value={formData.bio}
              onChange={(e) => handleChange('bio', e.target.value)}
              placeholder="Expert bio and qualifications"
              rows={3}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Photo URL
            </label>
            <Input
              value={formData.photo_url}
              onChange={(e) => handleChange('photo_url', e.target.value)}
              placeholder="https://example.com/photo.jpg"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Specialties (comma-separated)
            </label>
            <Input
              value={formData.specialties}
              onChange={(e) => handleChange('specialties', e.target.value)}
              placeholder="AI, ML, Cloud, etc."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Services (comma-separated)
            </label>
            <Input
              value={formData.services}
              onChange={(e) => handleChange('services', e.target.value)}
              placeholder="Consulting, Development, Training, etc."
            />
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => handleChange('is_active', e.target.checked)}
              className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
            />
            <label htmlFor="is_active" className="text-sm text-gray-700">
              Active Expert
            </label>
          </div>

          <div className="flex gap-2 pt-2">
            <Button
              type="submit"
              disabled={isSaving}
              className="flex items-center gap-2"
            >
              <Save className="w-4 h-4" />
              {isSaving ? 'Saving...' : 'Save Changes'}
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={onCancel}
              className="flex items-center gap-2"
            >
              <X className="w-4 h-4" />
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  )
}