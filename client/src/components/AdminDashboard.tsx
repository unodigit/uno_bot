import { useState, useEffect } from 'react'
import { Plus, UserPlus, Download, Search, Filter, Users, MessageSquare, Activity, Database, BarChart3, Clock, Edit2, Trash2, Star, ToggleLeft, ToggleRight, Type, X, Save, XCircle } from 'lucide-react'
import { Button } from './ui/Button'
import { Input } from './ui/Input'
import { Card } from './ui/Card'
import { ExpertCard } from './ExpertCard'
import { EditExpertForm } from './EditExpertForm'
import { AddExpertForm } from './AddExpertForm'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface AdminDashboardProps {
  onBack?: () => void
}

interface WelcomeTemplate {
  id: string;
  name: string;
  content: string;
  description: string | null;
  target_industry: string | null;
  is_default: boolean;
  is_active: boolean;
  use_count: number;
  created_at: string;
  updated_at: string;
}

export function AdminDashboard({ onBack }: AdminDashboardProps) {
  const [experts, setExperts] = useState([])
  const [analytics, setAnalytics] = useState<any>(null)
  const [templates, setTemplates] = useState<WelcomeTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [editingExpert, setEditingExpert] = useState(null)
  const [addingExpert, setAddingExpert] = useState(false)
  const [savingExpert, setSavingExpert] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [activeTab, setActiveTab] = useState<'experts' | 'templates'>('experts')
  const [addingTemplate, setAddingTemplate] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<WelcomeTemplate | null>(null)
  const [savingTemplate, setSavingTemplate] = useState(false)
  const [newTemplate, setNewTemplate] = useState({ name: '', content: '', description: '', target_industry: '', is_default: false, is_active: true })

  useEffect(() => {
    fetchExperts()
    fetchAnalytics()
    fetchTemplates()
  }, [])

  const fetchExperts = async () => {
    try {
      setLoading(true)
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/experts`)
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
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/analytics`)
      const data = await response.json()
      setAnalytics(data)
    } catch (error) {
      console.error('Failed to fetch analytics:', error)
    }
  }

  const fetchTemplates = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/templates`)
      const data = await response.json()
      setTemplates(data)
    } catch (error) {
      console.error('Failed to fetch templates:', error)
    }
  }

  const handleAddExpert = () => {
    setAddingExpert(true)
  }

  const handleSaveNewExpert = async (expertData: any) => {
    try {
      setSavingExpert(true)
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/experts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/experts/${editingExpert.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
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
        await fetch(`${API_BASE_URL}/api/v1/admin/experts/${expertId}`, {
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
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/experts`)
      const data = await response.json()

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

  const totalExperts = experts.length
  const activeExperts = experts.filter((e: any) => e.is_active).length
  const inactiveExperts = totalExperts - activeExperts

  // Template Management Functions
  const handleAddTemplate = () => {
    setNewTemplate({ name: '', content: '', description: '', target_industry: '', is_default: false, is_active: true })
    setAddingTemplate(true)
  }

  const handleSaveNewTemplate = async () => {
    try {
      setSavingTemplate(true)
      const response = await fetch(`${API_BASE_URL}/api/v1/templates`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTemplate),
      })

      if (!response.ok) {
        throw new Error('Failed to create template')
      }

      const created = await response.json()
      setTemplates(prev => [created, ...prev])
      setAddingTemplate(false)
    } catch (error) {
      console.error('Failed to create template:', error)
      alert('Failed to create template. Please try again.')
    } finally {
      setSavingTemplate(false)
    }
  }

  const handleEditTemplate = (template: WelcomeTemplate) => {
    setEditingTemplate(template)
    setNewTemplate({
      name: template.name,
      content: template.content,
      description: template.description || '',
      target_industry: template.target_industry || '',
      is_default: template.is_default,
      is_active: template.is_active,
    })
  }

  const handleUpdateTemplate = async () => {
    if (!editingTemplate) return

    try {
      setSavingTemplate(true)
      const response = await fetch(`${API_BASE_URL}/api/v1/templates/${editingTemplate.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTemplate),
      })

      if (!response.ok) {
        throw new Error('Failed to update template')
      }

      const updated = await response.json()
      setTemplates(prev => prev.map(t => t.id === editingTemplate.id ? updated : t))
      setEditingTemplate(null)
    } catch (error) {
      console.error('Failed to update template:', error)
      alert('Failed to update template. Please try again.')
    } finally {
      setSavingTemplate(false)
    }
  }

  const handleDeleteTemplate = async (templateId: string) => {
    if (confirm('Are you sure you want to delete this template?')) {
      try {
        await fetch(`${API_BASE_URL}/api/v1/templates/${templateId}`, {
          method: 'DELETE',
        })
        setTemplates(prev => prev.filter(t => t.id !== templateId))
      } catch (error) {
        console.error('Failed to delete template:', error)
        alert('Failed to delete template. Please try again.')
      }
    }
  }

  const handleToggleTemplateActive = async (template: WelcomeTemplate) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/templates/${template.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_active: !template.is_active }),
      })

      if (!response.ok) {
        throw new Error('Failed to toggle template')
      }

      const updated = await response.json()
      setTemplates(prev => prev.map(t => t.id === template.id ? updated : t))
    } catch (error) {
      console.error('Failed to toggle template:', error)
      alert('Failed to toggle template. Please try again.')
    }
  }

  const handleSetDefaultTemplate = async (template: WelcomeTemplate) => {
    try {
      for (const t of templates) {
        if (t.is_default) {
          const unsetResponse = await fetch(`${API_BASE_URL}/api/v1/templates/${t.id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ is_default: false }),
          })
          if (unsetResponse.ok) {
            const updated = await unsetResponse.json()
            setTemplates(prev => prev.map(x => x.id === t.id ? updated : x))
          }
        }
      }

      const response = await fetch(`${API_BASE_URL}/api/v1/templates/${template.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ is_default: true }),
      })

      if (!response.ok) {
        throw new Error('Failed to set default template')
      }

      const updated = await response.json()
      setTemplates(prev => prev.map(t => t.id === template.id ? updated : t))
    } catch (error) {
      console.error('Failed to set default template:', error)
      alert('Failed to set default template. Please try again.')
    }
  }

  const handleCancelTemplate = () => {
    setAddingTemplate(false)
    setEditingTemplate(null)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
              <p className="text-sm text-gray-600">Manage experts, templates, and system analytics</p>
            </div>
            <div className="flex items-center gap-3">
              {onBack && (
                <Button variant="outline" onClick={onBack} className="flex items-center gap-2">
                  ← Back to Chat
                </Button>
              )}
              {activeTab === 'experts' && (
                <Button onClick={handleAddExpert} className="flex items-center gap-2">
                  <UserPlus className="w-4 h-4" />
                  Add Expert
                </Button>
              )}
              {activeTab === 'templates' && !addingTemplate && !editingTemplate && (
                <Button onClick={handleAddTemplate} className="flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  Add Template
                </Button>
              )}
            </div>
          </div>
          {/* Tab Navigation */}
          <div className="flex gap-2 mt-4">
            <Button
              variant={activeTab === 'experts' ? 'primary' : 'outline'}
              onClick={() => setActiveTab('experts')}
              className="flex items-center gap-2"
            >
              <Users className="w-4 h-4" />
              Experts
            </Button>
            <Button
              variant={activeTab === 'templates' ? 'primary' : 'outline'}
              onClick={() => setActiveTab('templates')}
              className="flex items-center gap-2"
            >
              <Type className="w-4 h-4" />
              Welcome Templates
            </Button>
          </div>
        </div>
      </div>

      {/* Content Area */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Experts Tab */}
        {activeTab === 'experts' && (
          <>
            {/* Analytics Overview */}
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

            {/* Expert Controls */}
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
                    {filteredExperts.map((expert: any, index: number) => (
                      <ExpertCard
                        key={expert.id}
                        expert={expert}
                        index={index}
                        showActions={false}
                        showAdminActions={true}
                        onEdit={handleEditExpert}
                        onDelete={handleDeleteExpert}
                      />
                    ))}
                  </div>
                )}
              </div>
            </div>
          </>
        )}

        {/* Templates Tab */}
        {activeTab === 'templates' && (
          <>
            {/* Template Form (Add/Edit) */}
            {(addingTemplate || editingTemplate) && (
              <Card className="p-6 mb-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">
                    {addingTemplate ? 'Add New Template' : 'Edit Template'}
                  </h2>
                  <Button variant="outline" onClick={handleCancelTemplate} className="flex items-center gap-2">
                    <X className="w-4 h-4" />
                    Cancel
                  </Button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Template Name</label>
                    <Input
                      value={newTemplate.name}
                      onChange={(e) => setNewTemplate({ ...newTemplate, name: e.target.value })}
                      placeholder="e.g., Healthcare Welcome"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Target Industry</label>
                    <Input
                      value={newTemplate.target_industry}
                      onChange={(e) => setNewTemplate({ ...newTemplate, target_industry: e.target.value })}
                      placeholder="e.g., Healthcare (optional)"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Welcome Message Content</label>
                    <textarea
                      value={newTemplate.content}
                      onChange={(e) => setNewTemplate({ ...newTemplate, content: e.target.value })}
                      className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:outline-none"
                      rows={4}
                      placeholder="🎉 Welcome! I'm UnoBot, your AI business consultant..."
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                    <Input
                      value={newTemplate.description || ''}
                      onChange={(e) => setNewTemplate({ ...newTemplate, description: e.target.value })}
                      placeholder="Brief description of when to use this template"
                    />
                  </div>
                  <div className="flex items-center gap-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={newTemplate.is_default}
                        onChange={(e) => setNewTemplate({ ...newTemplate, is_default: e.target.checked })}
                        className="w-4 h-4"
                      />
                      <span className="text-sm text-gray-700">Default Template</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={newTemplate.is_active}
                        onChange={(e) => setNewTemplate({ ...newTemplate, is_active: e.target.checked })}
                        className="w-4 h-4"
                      />
                      <span className="text-sm text-gray-700">Active</span>
                    </label>
                  </div>
                </div>
                <div className="flex gap-2 mt-4">
                  <Button
                    onClick={addingTemplate ? handleSaveNewTemplate : handleUpdateTemplate}
                    disabled={savingTemplate || !newTemplate.name || !newTemplate.content}
                    className="flex items-center gap-2"
                  >
                    <Save className="w-4 h-4" />
                    {savingTemplate ? 'Saving...' : 'Save Template'}
                  </Button>
                </div>
              </Card>
            )}

            {/* Templates List */}
            <div className="bg-white rounded-lg shadow-sm border">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Welcome Message Templates</h2>
                <p className="text-sm text-gray-600 mt-1">Configure customizable welcome messages for different industries</p>
              </div>

              <div className="p-6">
                {templates.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No templates yet. Create your first welcome message template.
                  </div>
                ) : (
                  <div className="space-y-4">
                    {templates.map((template) => (
                      <Card key={template.id} className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h3 className="text-md font-semibold text-gray-900">{template.name}</h3>
                              {template.is_default && (
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">
                                  <Star className="w-3 h-3 mr-1" />
                                  Default
                                </span>
                              )}
                              {template.is_active ? (
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                                  Active
                                </span>
                              ) : (
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">
                                  Inactive
                                </span>
                              )}
                              {template.target_industry && (
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                  {template.target_industry}
                                </span>
                              )}
                            </div>
                            {template.description && (
                              <p className="text-sm text-gray-600 mb-2">{template.description}</p>
                            )}
                            <div className="text-sm text-gray-500 bg-gray-50 p-2 rounded font-mono max-h-24 overflow-y-auto">
                              {template.content}
                            </div>
                            <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                              <span>Used: {template.use_count} times</span>
                              <span>Created: {new Date(template.created_at).toLocaleDateString()}</span>
                            </div>
                          </div>
                          <div className="flex items-center gap-2 ml-4">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleEditTemplate(template)}
                              className="flex items-center gap-1"
                            >
                              <Edit2 className="w-3 h-3" />
                              Edit
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleToggleTemplateActive(template)}
                              className="flex items-center gap-1"
                            >
                              {template.is_active ? <ToggleRight className="w-3 h-3" /> : <ToggleLeft className="w-3 h-3" />}
                              {template.is_active ? 'Deactivate' : 'Activate'}
                            </Button>
                            {!template.is_default && (
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleSetDefaultTemplate(template)}
                                className="flex items-center gap-1"
                              >
                                <Star className="w-3 h-3" />
                                Set Default
                              </Button>
                            )}
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDeleteTemplate(template.id)}
                              className="flex items-center gap-1 text-red-600 hover:text-red-700"
                            >
                              <Trash2 className="w-3 h-3" />
                              Delete
                            </Button>
                          </div>
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </>
        )}
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
