'use client'

import { CalendarCheck, CheckCircle2, Mail, ShieldCheck } from 'lucide-react'
import { useRouter } from 'next/navigation'
import { useEffect } from 'react'

import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { useAuth } from '@/features/auth/auth-provider'

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

  useEffect(() => {
    if (!loading && !user) router.replace('/semana/login')
  }, [loading, router, user])

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

      <div className="mt-6 grid gap-4 sm:grid-cols-2">
        <section className="rounded-none border-[6px] border-white bg-card p-6 text-card-foreground shadow-[0_7px_0_hsl(var(--semana-contrast))]">
          <ShieldCheck aria-hidden="true" className="mb-4" />
          <h2 className="font-semibold">Dados da conta</h2>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            O perfil básico já está preparado para receber os dados do endpoint de usuário
            atual.
          </p>
        </section>
        <section className="rounded-none border-[6px] border-dashed border-[hsl(var(--semana-contrast))] bg-muted p-6 text-card-foreground">
          <CalendarCheck aria-hidden="true" className="mb-4" />
          <h2 className="font-semibold">Participação no evento</h2>
          <p className="mt-2 text-sm leading-6 text-muted-foreground">
            Presenças, certificados e pontuação aparecerão aqui quando esses recursos
            estiverem disponíveis.
          </p>
        </section>
      </div>
    </main>
  )
}
