'use client'

import { CalendarCheck, CheckCircle2, Clock3, Mail, Trophy } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { useAuth } from '@/features/auth/auth-provider'
import { getMyParticipation, type Participation } from '@/features/semana/api'

function initials(name: string) {
  return name
    .split(' ')
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()
}

export function ProfilePage() {
  const router = useRouter()
  const { user, loading } = useAuth()
  const [participation, setParticipation] = useState<Participation>()
  const [participationError, setParticipationError] = useState('')

  useEffect(() => {
    if (!loading && !user) router.replace('/semana/login')
  }, [loading, router, user])

  useEffect(() => {
    if (!user) return
    getMyParticipation()
      .then(setParticipation)
      .catch((reason: Error) => setParticipationError(reason.message))
  }, [user])

  if (loading || !user) {
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
          Sua conta
        </p>
        <h1 className="font-[family-name:var(--font-semana-display)] text-4xl font-bold uppercase tracking-tight">
          Perfil
        </h1>
      </div>

      <section className="rounded-none border-[8px] border-white bg-card p-6 text-card-foreground shadow-[0_10px_0_hsl(var(--semana-contrast))] sm:p-8">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
          <Avatar className="h-20 w-20">
            <AvatarFallback className="text-xl font-semibold">
              {initials(user.name)}
            </AvatarFallback>
          </Avatar>
          <div className="min-w-0 flex-1">
            <h2 className="text-2xl font-semibold">{user.name}</h2>
            <p className="mt-1 inline-flex items-center gap-2 text-muted-foreground">
              <Mail aria-hidden="true" size={16} />
              {user.email}
            </p>
          </div>
          <span className="inline-flex w-fit items-center gap-2 rounded-full border px-3 py-1 text-sm font-medium">
            <CheckCircle2 aria-hidden="true" size={16} />
            {user.isVerified ? 'Conta verificada' : 'Verificação pendente'}
          </span>
        </div>
      </section>

      <div className="mt-6">
        <section className="rounded-none border-[6px] border-[hsl(var(--semana-contrast))] bg-muted p-6 text-card-foreground">
          <CalendarCheck aria-hidden="true" className="mb-4" />
          <h2 className="font-semibold">Participação no evento</h2>
          {participationError ? (
            <p className="mt-2 text-sm leading-6 text-destructive">
              {participationError}
            </p>
          ) : participation ? (
            <>
              <div className="mt-4 grid grid-cols-2 gap-3">
                <ParticipationMetric
                  icon={Trophy}
                  label="Pontos"
                  value={participation.pontos}
                />
                <ParticipationMetric
                  icon={Clock3}
                  label="Horas"
                  value={participation.horas}
                />
              </div>
              <div className="mt-5 space-y-3">
                {participation.semanas.map((semana) => (
                  <div
                    className="rounded-md border border-white/70 bg-white/50 p-3"
                    key={semana.semana_id}
                  >
                    <div className="flex items-center justify-between gap-3 text-sm">
                      <span className="font-semibold">
                        {semana.nome} ({semana.ano})
                      </span>
                      <span>
                        {semana.pontos} pts · {semana.horas}h
                      </span>
                    </div>
                  </div>
                ))}
                {!participation.semanas.length && (
                  <p className="text-sm text-muted-foreground">
                    Nenhuma participação registrada.
                  </p>
                )}
              </div>
            </>
          ) : (
            <p className="mt-2 text-sm leading-6 text-muted-foreground">
              Carregando participação…
            </p>
          )}
        </section>
      </div>
    </main>
  )
}

function ParticipationMetric({
  icon: Icon,
  label,
  value,
}: {
  icon: typeof Trophy
  label: string
  value: number
}) {
  return (
    <div className="border border-white/70 bg-white/50 p-3">
      <Icon aria-hidden="true" size={18} />
      <p className="mt-2 text-2xl font-bold">{value}</p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </div>
  )
}
