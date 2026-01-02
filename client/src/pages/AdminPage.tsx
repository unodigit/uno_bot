import React, { useState } from 'react'
import { AdminDashboard } from '../components/AdminDashboard'

export default function AdminPage() {
  const [showDashboard, setShowDashboard] = useState(true)

  if (!showDashboard) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Admin Authentication Required</h1>
          <p className="text-gray-600 mb-8">Please log in to access the admin dashboard.</p>
          <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700">
            Login
          </button>
        </div>
      </div>
    )
  }

  return <AdminDashboard onBack={() => window.history.back()} />
}