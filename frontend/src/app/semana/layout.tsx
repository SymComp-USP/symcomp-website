import type { Metadata } from 'next'
import type { ReactNode } from 'react'

import { SemanaShell } from '@/features/semana/components/semana-shell'

interface SemanaLayoutProps {
  children: ReactNode
}

export const metadata: Metadata = {
  title: 'SYMCOMP | Semana da Computação',
  description: 'A Semana da Computação é o evento anual da SymComp no IME USP.',
}

export default function SemanaLayout({ children }: SemanaLayoutProps) {
  return <SemanaShell>{children}</SemanaShell>
}
