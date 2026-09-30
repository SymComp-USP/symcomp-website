'use client'

import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

import { useAuth } from '@/features/auth/auth-provider'

import { getSemanaRanking, listSemanas, type SemanaRankingEntry } from '../api'

export function RankingPage() {
  const router = useRouter()
  const { loading: authLoading, user } = useAuth()
  const [eventName, setEventName] = useState<string>()
  const [ranking, setRanking] = useState<SemanaRankingEntry[]>([])
  const [error, setError] = useState<string>()

  useEffect(() => {
    if (authLoading) return
    if (!user) {
      router.replace('/semana/login')
      return
    }

    async function loadRanking() {
      try {
        const events = await listSemanas()
        const event = events[0]
        if (!event) {
          setError('Ainda não há uma Semana cadastrada.')
          return
        }

        setEventName(`${event.nome} ${event.ano}`)
        setRanking(await getSemanaRanking(event.id))
      } catch {
        setError('Não foi possível carregar o ranking.')
      }
    }

    loadRanking()
  }, [authLoading, router, user])

  if (authLoading || !user) {
    return (
      <main className="mx-auto min-h-[calc(100svh-65px)] max-w-4xl px-6 py-16">
        Carregando…
      </main>
    )
  }

  return (
    <main className="mx-auto min-h-[calc(100svh-65px)] max-w-4xl px-6 py-16">
      <div className="mb-10 space-y-3">
        <p className="font-[family-name:var(--font-semana-display)] text-sm font-bold uppercase tracking-[0.2em] text-primary">
          {eventName ?? 'Semana da Computação'}
        </p>
        <h1 className="font-[family-name:var(--font-semana-display)] text-4xl font-bold uppercase tracking-tight sm:text-5xl">
          Ranking
        </h1>
        <p className="text-xl text-white/80">Pontuação acumulada no evento.</p>
      </div>

      {error ? (
        <p className="text-destructive">{error}</p>
      ) : ranking.length === 0 ? (
        <p>Ainda não há participantes pontuando.</p>
      ) : (
        <ol className="space-y-3">
          {ranking.map((entry, index) => (
            <li
              className="flex items-center justify-between border-[6px] border-white bg-card px-5 py-4 text-card-foreground shadow-[0_5px_0_hsl(var(--semana-contrast))]"
              key={entry.participant_id}
            >
              <span className="flex items-center gap-4">
                <span className="font-[family-name:var(--font-semana-display)] text-xl text-primary">
                  {index + 1}
                </span>
                <span className="text-lg font-semibold">{entry.nickname}</span>
              </span>
              <span className="font-[family-name:var(--font-semana-display)] text-lg">
                {entry.points} pts
              </span>
            </li>
          ))}
        </ol>
      )}
    </main>
  )
}
