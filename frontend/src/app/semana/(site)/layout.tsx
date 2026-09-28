import { redirect } from 'next/navigation'
import type { ReactNode } from 'react'

import { SemanaShell } from '@/features/semana/components/semana-shell'
import { SEMANA_PREVIEW_MODE } from '@/features/semana/config'

export default function SemanaSiteLayout({ children }: { children: ReactNode }) {
  if (SEMANA_PREVIEW_MODE) {
    redirect('/semana')
  }

  return <SemanaShell>{children}</SemanaShell>
}
