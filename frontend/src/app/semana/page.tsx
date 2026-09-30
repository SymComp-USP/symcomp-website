'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

import { SemanaButton } from '@/features/semana/components/semana-button'

export default function SemanaPage() {
  const router = useRouter()
  const [starting, setStarting] = useState(false)

  useEffect(() => {
    if (!starting) return
    const timer = window.setTimeout(() => router.push('/semana/inicio'), 700)
    return () => window.clearTimeout(timer)
  }, [router, starting])

  return (
    <main className="flex min-h-svh flex-col items-center justify-center bg-[#110f0f] px-6 text-white">
      <div className="flex w-full max-w-2xl flex-col items-center gap-8 text-center">
        <p className="font-[family-name:var(--font-semana-display)] text-sm uppercase tracking-[0.25em] text-primary">
          Semana da Computação 2026
        </p>
        <h1 className="font-[family-name:var(--font-semana-display)] text-4xl font-bold uppercase sm:text-6xl">
          Em breve
        </h1>
        <p className="max-w-xl text-lg text-white/75 sm:text-xl">
          Estamos preparando uma nova edição do evento. Conheça a página inicial para
          acompanhar as novidades.
        </p>
        <SemanaButton disabled={starting} onClick={() => setStarting(true)}>
          {starting ? 'Carregando…' : 'Começar'}
        </SemanaButton>
      </div>
    </main>
  )
}
