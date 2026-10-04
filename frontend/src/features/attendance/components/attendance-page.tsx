'use client'

import { useEffect, useState, type FormEvent } from 'react'

import { useAuth } from '@/features/auth/auth-provider'
import { registerAttendance, listSemanas, type Semana } from '@/features/semana/api'
import { SemanaButton } from '@/features/semana/components/semana-button'
import { SemanaInput } from '@/features/semana/components/semana-input'

export function AttendancePage() {
  const { user, loading: authLoading } = useAuth()
  const [semana, setSemana] = useState<Semana>()
  const [loading, setLoading] = useState(true)
  const [code, setCode] = useState('')
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState<string>()
  const [error, setError] = useState<string>()

  useEffect(() => {
    listSemanas()
      .then((semanas) => {
        // Temporary fallback: replace with backend-provided active/current Semana
        // before future editions coexist, or a future edition may win here.
        const latest = [...semanas].sort((a, b) => b.ano - a.ano)[0]
        if (!latest) throw new Error('Nenhuma Semana disponível.')
        setSemana(latest)
      })
      .catch((cause: unknown) => {
        setError(
          cause instanceof Error ? cause.message : 'Não foi possível carregar a Semana.',
        )
      })
      .finally(() => setLoading(false))
  }, [])

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setMessage(undefined)
    setError(undefined)

    if (!semana || !/^\d{4}$/.test(code)) {
      setError('Digite o código de 4 dígitos.')
      return
    }

    try {
      const result = await registerAttendance(
        semana.id,
        code,
        user ? {} : { nome: name, email },
      )
      setMessage(
        result.pontos_adicionados > 0
          ? `Presença registrada. +${result.pontos_adicionados} pontos.`
          : 'Presença registrada.',
      )
      setCode('')
    } catch (cause: unknown) {
      setError(
        cause instanceof Error ? cause.message : 'Não foi possível registrar presença.',
      )
    }
  }

  const pageLoading = authLoading || loading

  return (
    <main className="mx-auto flex min-h-[calc(100svh-65px)] max-w-6xl items-start justify-center px-6 py-10 sm:py-16">
      <section className="w-full max-w-md space-y-8 text-foreground">
        <div className="space-y-2 text-center">
          <h1 className="font-[family-name:var(--font-semana-display)] text-4xl font-bold uppercase tracking-tight">
            Presença
          </h1>
          <p className="mx-auto max-w-xs font-[family-name:var(--font-semana-body)] text-lg text-[hsl(var(--semana-contrast))]">
            Digite o código mostrado na atividade.
          </p>
        </div>

        <form className="space-y-5" onSubmit={submit}>
          <label className="block space-y-2" htmlFor="attendance-code">
            <span className="text-sm font-medium">Código</span>
            <SemanaInput
              autoComplete="one-time-code"
              id="attendance-code"
              inputMode="numeric"
              maxLength={4}
              onChange={(event) =>
                setCode(event.target.value.replace(/\D/g, '').slice(0, 4))
              }
              pattern="[0-9]{4}"
              placeholder="0000"
              required
              value={code}
            />
          </label>

          {!authLoading && !user && (
            <div className="space-y-5">
              <label className="block space-y-2" htmlFor="attendance-name">
                <span className="text-sm font-medium">Nome</span>
                <SemanaInput
                  autoComplete="name"
                  id="attendance-name"
                  onChange={(event) => setName(event.target.value)}
                  required
                  value={name}
                />
              </label>
              <label className="block space-y-2" htmlFor="attendance-email">
                <span className="text-sm font-medium">E-mail</span>
                <SemanaInput
                  autoComplete="email"
                  id="attendance-email"
                  onChange={(event) => setEmail(event.target.value)}
                  required
                  type="email"
                  value={email}
                />
              </label>
            </div>
          )}

          {error && (
            <p className="text-sm text-destructive" role="alert">
              {error}
            </p>
          )}
          {message && (
            <p className="text-sm text-[hsl(var(--semana-contrast))]" role="status">
              {message}
            </p>
          )}

          <SemanaButton className="w-full" disabled={pageLoading} type="submit">
            {pageLoading ? 'Carregando…' : 'Registrar presença'}
          </SemanaButton>
        </form>

        {semana && (
          <p className="text-center text-sm text-[hsl(var(--semana-contrast))]/70">
            Semana {semana.ano}
          </p>
        )}
      </section>
    </main>
  )
}
