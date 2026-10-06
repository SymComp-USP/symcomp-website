'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'

import { verifyEmail } from '@/features/auth/api'
import { AuthNotice } from './auth-notice'

export function VerifyEmailPage({ token }: { token?: string }) {
  const [message, setMessage] = useState('Verificando seu e-mail…')
  const [error, setError] = useState(false)

  useEffect(() => {
    if (!token) {
      setError(true)
      setMessage('Link de verificação inválido.')
      return
    }

    verifyEmail(token)
      .then(() => setMessage('E-mail verificado. Agora você já pode entrar.'))
      .catch(() => {
        setError(true)
        setMessage('Link inválido, expirado ou já utilizado.')
      })
  }, [token])

  return (
    <main className="mx-auto flex min-h-[calc(100svh-65px)] max-w-6xl items-start justify-center px-6 py-10 sm:py-16">
      <section className="w-full max-w-md space-y-6 text-center text-foreground">
        <h1 className="font-[family-name:var(--font-semana-display)] text-4xl font-bold uppercase tracking-tight">
          {error ? 'Verificação não concluída' : 'Verificação de e-mail'}
        </h1>
        <AuthNotice variant={error ? 'error' : 'success'}>{message}</AuthNotice>
        <Link className="font-medium underline underline-offset-4" href="/semana/login">
          Ir para login
        </Link>
      </section>
    </main>
  )
}
