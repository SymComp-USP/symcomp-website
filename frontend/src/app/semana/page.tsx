import { SemanaHome } from '@/features/semana/components/semana-home'
import { SemanaShell } from '@/features/semana/components/semana-shell'

export default function SemanaPage() {
  return (
    <SemanaShell>
      <SemanaHome />
    </SemanaShell>
  )
}
