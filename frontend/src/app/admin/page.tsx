import { AuthProvider } from '@/features/auth/auth-provider'
import { AdminPanel } from '@/features/admin/components/admin-panel'

export default function AdminPage() {
  return (
    <AuthProvider>
      <AdminPanel />
    </AuthProvider>
  )
}
