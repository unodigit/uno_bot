import { useState, useEffect } from 'react'
import { Plus, UserPlus, Edit, Trash2, Download, Search, Filter, Calendar, Users, MessageSquare } from 'lucide-react'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Card } from '../components/ui/Card'
import { ExpertCard } from './ExpertCard'

interface AdminDashboardProps {
  onBack?: () => void
}

export function AdminDashboard({ onBack }: AdminDashboardProps) {
  const [experts, setExperts] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')

  useEffect(() => {
    fetchExperts()
  }, [])

  const fetchExperts = async () => {
    try {
      setLoading(true)
      const response = await fetch('/api/v1/admin/experts')
      const data = await response.json()
      setExperts(data)
    } catch (error) {
      console.error('Failed to fetch experts:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteExpert = async (expertId: string) => {
    if (confirm('Are you sure you want to delete this expert?')) {
      try {
        await fetch(`/api/v1/admin/experts/${expertId}`, {
          method: 'DELETE',
        })
        fetchExperts()
      } catch (error) {
        console.error('Failed to delete expert:', error)
      }
    }
  }

  const filteredExperts = experts.filter((expert) => {
    const matchesSearch = expert.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         expert.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         expert.role.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesStatus = filterStatus === 'all' || (filterStatus === 'active' && expert.is_active) || (filterStatus === 'inactive' && !expert.is_active)

    return matchesSearch && matchesStatus
  })

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-sm text-gray-600">Manage experts and system analytics</p>
            </div>
            <div className="flex items-center gap-3">
              {onBack && (
                <Button variant="outline" onClick={onBack} className="flex items-center gap-2">
                  ← Back to Chat
                </Button>
              )}
              <Button onClick={() => {}} className="flex items-center gap-2">
                <UserPlus className="w-4 h-4" />
                Add Expert
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Analytics Overview */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Experts</p>
                <p className="text-2xl font-bold text-gray-900">{experts.length}</p>
              </div>
              <Users className="w-8 h-8 text-blue-600" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Experts</p>
                <p className="text-2xl font-bold text-gray-900">{experts.filter(e => e.is_active).length}</p>
              </div>
              <Calendar className="w-8 h-8 text-green-600" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Bookings Today</p>
                <p className="text-2xl font-bold text-gray-900">--</p>
              </div>
              <MessageSquare className="w-8 h-8 text-purple-600" />
            </div>
          </Card>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-lg shadow-sm border p-4 mb-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  type="text"
                  placeholder="Search experts by name, email, or role..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                variant={filterStatus === 'all' ? 'primary' : 'outline'}
                onClick={() => setFilterStatus('all')}
                className="flex items-center gap-2"
              >
                <Filter className="w-4 h-4" />
                All
              </Button>
              <Button
                variant={filterStatus === 'active' ? 'primary' : 'outline'}
                onClick={() => setFilterStatus('active')}
                className="flex items-center gap-2"
              >
                Active
              </Button>
              <Button
                variant={filterStatus === 'inactive' ? 'primary' : 'outline'}
                onClick={() => setFilterStatus('inactive')}
                className="flex items-center gap-2"
              >
                Inactive
              </Button>
            </div>
            <Button onClick={() => {}} className="flex items-center gap-2">
              <Download className="w-4 h-4" />
              Export CSV
            </Button>
          </div>
        </div>

        {/* Experts List */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Expert Management</h2>
            <p className="text-sm text-gray-600 mt-1">Manage UnoDigit expert profiles and availability</p>
          </div>

          <div className="p-6">
            {loading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>
            ) : filteredExperts.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                No experts found. {experts.length === 0 ? 'Start by adding your first expert.' : 'Try adjusting your search or filter.'}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredExperts.map((expert) => (
                  <div key={expert.id} className="relative group">
                    <ExpertCard expert={expert} showActions={true} />
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => { /* Edit expert */ }}
                        className="flex items-center gap-1"
                      >
                        <Edit className="w-3 h-3" />
                        Edit
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={() => handleDeleteExpert(expert.id)}
                        className="flex items-center gap-1"
                      >
                        <Trash2 className="w-3 h-3" />
                        Delete
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}