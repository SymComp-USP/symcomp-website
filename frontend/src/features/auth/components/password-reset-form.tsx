'use client'

import { useState, type FormEvent } from 'react'

import { confirmPasswordReset, requestPasswordReset } from '@/features/auth/api'
import { SemanaButton } from '@/features/semana/components/semana-button'
import { SemanaInput } from '@/features/semana/components/semana-input'
import { AuthNotice } from './auth-notice'

export function PasswordResetForm({ token }: { token?: string }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmation, setConfirmation] = useState('')
  const [message, setMessage] = useState<string>()
  const [error, setError] = useState<string>()
  const [loading, setLoading] = useState(false)

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(undefined)
    setMessage(undefined)
    setLoading(true)

    try {
      if (token) {
        if (password.length < 8) {
          throw new Error('A senha deve ter pelo menos 8 caracteres.')
        }
        if (password !== confirmation) {
          throw new Error('As senhas não coincidem.')
        }
        await confirmPasswordReset(token, password)
        setMessage('Senha redefinida. Você já pode entrar.')
      } else {
        await requestPasswordReset(email)
        setMessage('Se o e-mail existir, enviaremos um link de redefinição.')
      }
    } catch (caught) {
      setError(
        caught instanceof Error
          ? caught.message
          : 'Não foi possível concluir a operação.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="space-y-5" onSubmit={submit}>
      {token ? (
        <>
          <label className="block space-y-2 text-sm font-medium" htmlFor="password">
            Nova senha
            <SemanaInput
              autoComplete="new-password"
              id="password"
              minLength={8}
              onChange={(event) => setPassword(event.target.value)}
              required
              type="password"
              value={password}
            />
          </label>
          <label className="block space-y-2 text-sm font-medium" htmlFor="confirmation">
            Confirmar senha
            <SemanaInput
              autoComplete="new-password"
              id="confirmation"
              onChange={(event) => setConfirmation(event.target.value)}
              required
              type="password"
              value={confirmation}
            />
          </label>
        </>
      ) : (
        <label className="block space-y-2 text-sm font-medium" htmlFor="email">
          E-mail
          <SemanaInput
            autoComplete="email"
            id="email"
            onChange={(event) => setEmail(event.target.value)}
            required
            type="email"
            value={email}
          />
        </label>
      )}
      {error && <AuthNotice variant="error">{error}</AuthNotice>}
      {message && <AuthNotice>{message}</AuthNotice>}
      <SemanaButton className="w-full" disabled={loading} type="submit">
        {loading ? 'Enviando…' : token ? 'Redefinir senha' : 'Enviar link'}
      </SemanaButton>
    </form>
  )
}
