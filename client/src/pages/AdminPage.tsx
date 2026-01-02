import { AdminDashboard } from '../components/AdminDashboard'

export default function AdminPage() {
  return <AdminDashboard onBack={() => window.history.back()} />
}