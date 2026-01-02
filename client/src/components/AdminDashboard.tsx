import { useState, useEffect } from 'react'
import { Plus, UserPlus, Edit, Trash2, Download, Search, Filter, Calendar, Users, MessageSquare, Activity, Database, BarChart3, TrendingUp, Eye, Clock, DollarSign, Users2, DatabaseBackup, DatabaseZap } from 'lucide-react'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Card } from '../components/ui/Card'
import { ExpertCard } from './ExpertCard'
import { EditExpertForm } from './EditExpertForm'
import { AddExpertForm } from './AddExpertForm'

interface AdminDashboardProps {
  onBack?: () => void
}

export function AdminDashboard({ onBack }: AdminDashboardProps) {
  const [experts, setExperts] = useState([])
  const [analytics, setAnalytics] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [editingExpert, setEditingExpert] = useState(null)
  const [addingExpert, setAddingExpert] = useState(false)
  const [savingExpert, setSavingExpert] = useState(false)
  const [exporting, setExporting] = useState(false)

  useEffect(() => {
    fetchExperts()
    fetchAnalytics()
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

  const fetchAnalytics = async () => {
    try {
      const response = await fetch('/api/v1/admin/analytics')
      const data = await response.json()
      setAnalytics(data)
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
    }
  }

  const handleAddExpert = () => {
    setAddingExpert(true)
  }

  const handleSaveNewExpert = async (expertData: any) => {
    try {
      setSavingExpert(true)
      const response = await fetch('/api/v1/admin/experts', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(expertData),
      })

      if (!response.ok) {
        throw new Error('Failed to create expert')
      }

      const newExpert = await response.json()
      setExperts(prev => [...prev, newExpert])
      setAddingExpert(false)
    } catch (error) {
      console.error('Failed to create expert:', error)
      alert('Failed to create expert. Please try again.')
    } finally {
      setSavingExpert(false)
    }
  }

  const handleCancelAdd = () => {
    setAddingExpert(false)
  }

  const handleEditExpert = (expert: any) => {
    setEditingExpert(expert)
  }

  const handleSaveExpert = async (updatedExpert: any) => {
    if (!editingExpert) return

    try {
      setSavingExpert(true)
      const response = await fetch(`/api/v1/admin/experts/${editingExpert.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedExpert),
      })

      if (!response.ok) {
        throw new Error('Failed to update expert')
      }

      const updatedData = await response.json()
      setExperts(prev => prev.map(exp => exp.id === editingExpert.id ? updatedData : exp))
      setEditingExpert(null)
    } catch (error) {
      console.error('Failed to save expert:', error)
      alert('Failed to save expert. Please try again.')
    } finally {
      setSavingExpert(false)
    }
  }

  const handleCancelEdit = () => {
    setEditingExpert(null)
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

  const handleExportCSV = async () => {
    try {
      setExporting(true)
      // Get all experts with full details
      const response = await fetch('/api/v1/admin/experts')
      const data = await response.json()

      // Generate CSV
      const headers = ['Name', 'Email', 'Role', 'Active', 'Specialties', 'Services']
      const rows = data.map((expert: any) => [
        expert.name,
        expert.email,
        expert.role,
        expert.is_active ? 'Yes' : 'No',
        expert.specialties?.join('; ') || '',
        expert.services?.join('; ') || '',
      ])

      const csvContent = [
        headers.join(','),
        ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
      ].join('\n')

      // Download
      const blob = new Blob([csvContent], { type: 'text/csv' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `experts_${new Date().toISOString().split('T')[0]}.csv`
      a.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to export CSV:', error)
      alert('Failed to export CSV. Please try again.')
    } finally {
      setExporting(false)
    }
  }

  const filteredExperts = experts.filter((expert) => {
    const matchesSearch = expert.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         expert.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         expert.role.toLowerCase().includes(searchTerm.toLowerCase())

    const matchesStatus = filterStatus === 'all' || (filterStatus === 'active' && expert.is_active) || (filterStatus === 'inactive' && !expert.is_active)

    return matchesSearch && matchesStatus
  })

  // Calculate analytics from data
  const totalExperts = experts.length
  const activeExperts = experts.filter((e: any) => e.is_active).length
  const inactiveExperts = totalExperts - activeExperts

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
              <Button onClick={handleAddExpert} className="flex items-center gap-2">
                <UserPlus className="w-4 h-4" />
                Add Expert
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Analytics Overview */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Experts</p>
                <p className="text-2xl font-bold text-gray-900">{totalExperts}</p>
              </div>
              <Users className="w-8 h-8 text-blue-600" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Experts</p>
                <p className="text-2xl font-bold text-gray-900">{activeExperts}</p>
              </div>
              <Activity className="w-8 h-8 text-green-600" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Inactive Experts</p>
                <p className="text-2xl font-bold text-gray-900">{inactiveExperts}</p>
              </div>
              <Database className="w-8 h-8 text-orange-600" />
            </div>
          </Card>

          <Card className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">System Status</p>
                <p className="text-2xl font-bold text-green-600">
                  {analytics?.system?.status ? 'Operational' : 'Checking...'}
                </p>
              </div>
              <MessageSquare className="w-8 h-8 text-purple-600" />
            </div>
          </Card>
        </div>

        {/* Detailed Analytics */}
        {analytics && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            {/* Conversation Analytics */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Conversation Analytics (30 days)</h3>
                <BarChart3 className="w-6 h-6 text-blue-600" />
              </div>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">{analytics.conversations?.sessions?.total || 0}</div>
                    <div className="text-sm text-blue-800">Total Sessions</div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{analytics.conversations?.sessions?.completed || 0}</div>
                    <div className="text-sm text-green-800">Completed</div>
                  </div>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Abandoned:</span>
                    <span className="font-medium text-red-600">{analytics.conversations?.sessions?.abandoned || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Completion Rate:</span>
                    <span className="font-medium">{(analytics.conversations?.sessions?.completion_rate || 0).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">PRD Generated:</span>
                    <span className="font-medium">{analytics.conversations?.conversion_metrics?.sessions_with_prd || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">PRD Conversion:</span>
                    <span className="font-medium text-blue-600">{(analytics.conversations?.conversion_metrics?.prd_conversion_rate || 0).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Booking Conversion:</span>
                    <span className="font-medium text-purple-600">{(analytics.conversations?.conversion_metrics?.booking_conversion_rate || 0).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Avg Session Duration:</span>
                    <span className="font-medium">{(analytics.conversations?.engagement_metrics?.average_session_duration_minutes || 0).toFixed(0)} min</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Avg Lead Score:</span>
                    <span className="font-medium">{analytics.conversations?.engagement_metrics?.lead_score?.average || 0}</span>
                  </div>
                  {analytics.conversations?.service_analytics?.most_popular_service && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Most Popular Service:</span>
                      <span className="font-medium">{analytics.conversations?.service_analytics?.most_popular_service}</span>
                    </div>
                  )}
                </div>
              </div>
            </Card>

            {/* Booking Analytics */}
            <Card className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Booking Analytics (30 days)</h3>
                <Clock className="w-6 h-6 text-purple-600" />
              </div>
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
                  <div className="bg-purple-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">{analytics.bookings?.bookings?.total || 0}</div>
                    <div className="text-sm text-purple-800">Total Bookings</div>
                  </div>
                  <div className="bg-green-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">{analytics.bookings?.bookings?.confirmed || 0}</div>
                    <div className="text-sm text-green-800">Confirmed</div>
                  </div>
                  <div className="bg-orange-50 p-4 rounded-lg">
                    <div className="text-2xl font-bold text-orange-600">{analytics.bookings?.bookings?.cancelled || 0}</div>
                    <div className="text-sm text-orange-800">Cancelled</div>
                  </div>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Cancellation Rate:</span>
                    <span className="font-medium">{(analytics.bookings?.bookings?.cancellation_rate || 0).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Avg Lead Time:</span>
                    <span className="font-medium">{(analytics.bookings?.timing?.average_lead_time_days || 0).toFixed(1)} days</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Last 7 Days:</span>
                    <span className="font-medium">{analytics.bookings?.recent_trends?.last_7_days_bookings || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Recent Cancellations:</span>
                    <span className="font-medium text-red-600">{analytics.bookings?.recent_trends?.recent_cancellations || 0}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Recent Cancellation Rate:</span>
                    <span className="font-medium">{(analytics.bookings?.recent_trends?.recent_cancellation_rate || 0).toFixed(1)}%</span>
                  </div>
                </div>
              </div>
            </Card>

            {/* System Health */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">System Health</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Status:</span>
                  <span className={`font-medium ${analytics.system_health?.status === 'operational' ? 'text-green-600' : 'text-orange-600'}`}>
                    {analytics.system_health?.status || 'Unknown'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Database:</span>
                  <span className={`font-medium ${analytics.system_health?.database === 'healthy' ? 'text-green-600' : 'text-red-600'}`}>
                    {analytics.system_health?.database || 'Unknown'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Active Sessions:</span>
                  <span className="font-medium">{analytics.system_health?.metrics?.active_sessions || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">API Version:</span>
                  <span className="font-medium">{analytics.api?.version || '1.0.0'}</span>
                </div>
              </div>
            </Card>

            {/* Expert Performance */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Expert Performance (30 days)</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Experts:</span>
                  <span className="font-medium">{analytics.experts_performance?.summary?.total_experts || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Active Experts:</span>
                  <span className="font-medium text-green-600">{analytics.experts_performance?.summary?.active_experts || 0}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Avg Bookings/Expert:</span>
                  <span className="font-medium">{(analytics.experts_performance?.summary?.average_bookings_per_expert || 0).toFixed(1)}</span>
                </div>
              </div>
            </Card>
          </div>
        )}

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
            <Button onClick={handleExportCSV} disabled={exporting} className="flex items-center gap-2">
              <Download className="w-4 h-4" />
              {exporting ? 'Exporting...' : 'Export CSV'}
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
                {filteredExperts.map((expert: any) => (
                  <div key={expert.id} className="relative group">
                    <ExpertCard expert={expert} />
                    <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleEditExpert(expert)}
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

      {/* Add Expert Form */}
      {addingExpert && (
        <AddExpertForm
          onSave={handleSaveNewExpert}
          onCancel={handleCancelAdd}
          isSaving={savingExpert}
        />
      )}

      {/* Edit Expert Form */}
      {editingExpert && (
        <EditExpertForm
          expert={editingExpert}
          onSave={handleSaveExpert}
          onCancel={handleCancelEdit}
          isSaving={savingExpert}
        />
      )}
    </div>
  )
}
