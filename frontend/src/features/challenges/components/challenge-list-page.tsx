'use client'

import { ArrowUpRight, Clock3, Trophy } from 'lucide-react'
import Image from 'next/image'
import Link from 'next/link'
import { useEffect, useState } from 'react'

import { SemanaButton } from '@/features/semana/components/semana-button'

import { listChallenges, mediaUrl, type Challenge } from '../api'

const PAGE_SIZE = 20

const challengeTypeLabels: Record<Challenge['scoring_type'], string> = {
  input: 'Resposta livre',
  quiz: 'Quiz',
  manual: 'Desafio',
}

const deadlineFormatter = new Intl.DateTimeFormat('pt-BR', {
  dateStyle: 'medium',
  timeStyle: 'short',
  timeZone: 'America/Sao_Paulo',
})

export function ChallengeListPage() {
  const [challenges, setChallenges] = useState<Challenge[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [loadingMore, setLoadingMore] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    listChallenges(PAGE_SIZE)
      .then((page) => {
        if (active) {
          setChallenges(page.items)
          setTotal(page.total)
        }
      })
      .catch((reason: Error) => {
        if (active) setError(reason.message)
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [])

  async function loadMore() {
    setLoadingMore(true)
    setError('')
    try {
      const page = await listChallenges(PAGE_SIZE, challenges.length)
      setChallenges((current) => [...current, ...page.items])
      setTotal(page.total)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Não foi possível carregar.')
    } finally {
      setLoadingMore(false)
    }
  }

  return (
    <main className="mx-auto min-h-[calc(100svh-65px)] max-w-4xl px-6 py-16">
      <header className="mb-12 max-w-2xl space-y-3">
        <p className="font-[family-name:var(--font-semana-display)] text-sm font-bold uppercase tracking-[0.2em] text-primary">
          Semana da Computação
        </p>
        <h1 className="font-[family-name:var(--font-semana-display)] text-4xl font-bold uppercase tracking-tight sm:text-5xl">
          Desafios
        </h1>
        <p className="text-xl text-white/80">
          Explore os desafios e teste seus conhecimentos.
        </p>
      </header>

      {loading && <p role="status">Carregando desafios…</p>}
      {error && (
        <p className="mb-5 text-destructive" role="alert">
          {error}
        </p>
      )}
      {!loading && !error && !challenges.length && <p>Novos desafios em breve.</p>}

      <div className="space-y-5">
        {challenges.map((challenge) => (
          <Link
            aria-label={`Abrir desafio: ${challenge.title}`}
            className="group block border-[7px] border-white bg-card p-5 text-card-foreground shadow-[0_8px_0_hsl(var(--semana-contrast))] transition-transform hover:-translate-y-1 focus-visible:outline focus-visible:outline-4 focus-visible:outline-offset-4 focus-visible:outline-primary"
            href={`/semana/desafios/${challenge.id}`}
            key={challenge.id}
          >
            <div className="flex flex-col gap-5 sm:flex-row">
              {challenge.image_url && (
                <div className="relative aspect-[4/3] w-full shrink-0 overflow-hidden border-2 border-[hsl(var(--semana-contrast))] sm:w-44">
                  <Image
                    alt=""
                    className="object-cover"
                    fill
                    sizes="(max-width: 640px) 100vw, 176px"
                    src={mediaUrl(challenge.image_url)}
                    unoptimized
                  />
                </div>
              )}
              <div className="min-w-0 flex-1">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <p className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                      {challengeTypeLabels[challenge.scoring_type]}
                    </p>
                    <h2 className="mt-1 text-2xl font-bold leading-tight">
                      {challenge.title}
                    </h2>
                  </div>
                  <ArrowUpRight
                    aria-hidden="true"
                    className="shrink-0 transition-transform group-hover:translate-x-1 group-hover:-translate-y-1"
                    size={22}
                  />
                </div>
                {(challenge.description || challenge.prompt) && (
                  <p className="mt-3 line-clamp-3 text-sm leading-6 text-muted-foreground">
                    {challenge.description || challenge.prompt}
                  </p>
                )}
                <p className="mt-4 inline-flex items-center gap-2 text-sm font-medium text-muted-foreground">
                  {challenge.scoring_type === 'quiz' ? (
                    <Trophy aria-hidden="true" size={16} />
                  ) : (
                    <Clock3 aria-hidden="true" size={16} />
                  )}
                  Encerra em {deadlineFormatter.format(new Date(challenge.finishes_at))}
                </p>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {!loading && challenges.length < total && (
        <div className="mt-10 flex justify-center">
          <SemanaButton
            className="border-4 px-5 py-3 text-lg shadow-[0_4px_0_hsl(var(--semana-contrast))]"
            disabled={loadingMore}
            onClick={loadMore}
            type="button"
            variant="outline"
          >
            {loadingMore ? 'Carregando…' : 'Carregar mais desafios'}
          </SemanaButton>
        </div>
      )}
    </main>
  )
}
