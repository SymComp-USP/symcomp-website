'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { useAuth } from '@/features/auth/auth-provider'
import { AuthNotice } from './auth-notice'
import { SemanaButton } from '@/features/semana/components/semana-button'
import { SemanaInput } from '@/features/semana/components/semana-input'
import { resendVerification } from '../api'
import { OAuthButtons } from './oauth-buttons'

const schema = z.object({
  email: z.string().email('Digite um e-mail válido.'),
  password: z.string().min(8, 'A senha deve ter pelo menos 8 caracteres.'),
})

type Values = z.infer<typeof schema>

export function LoginForm() {
  const router = useRouter()
  const { loading, login, user } = useAuth()
  const [error, setError] = useState<string>()
  const [resendMessage, setResendMessage] = useState<string>()
  const [resending, setResending] = useState(false)
  const form = useForm<Values>({
    resolver: zodResolver(schema),
    defaultValues: { email: '', password: '' },
  })

  useEffect(() => {
    if (!loading && user) router.replace('/semana/perfil')
  }, [loading, router, user])

  if (loading || user) return <p>{user ? 'Você já está conectado.' : 'Carregando…'}</p>

  async function submit(values: Values) {
    setError(undefined)
    setResendMessage(undefined)
    try {
      const user = await login(values)
      router.push(user?.isAdmin ? '/admin' : '/semana/perfil')
    } catch {
      setError('Não foi possível entrar. Verifique seus dados ou confirme seu e-mail.')
    }
  }

  async function resend() {
    setResending(true)
    setResendMessage(undefined)
    try {
      await resendVerification(form.getValues('email'))
      setResendMessage('Se sua conta precisar de verificação, enviaremos um e-mail.')
    } finally {
      setResending(false)
    }
  }

  return (
    <Form {...form}>
      <div className="mb-5">
        <OAuthButtons />
      </div>
      <form className="space-y-5" onSubmit={form.handleSubmit(submit)}>
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>E-mail</FormLabel>
              <FormControl>
                <SemanaInput
                  autoComplete="email"
                  placeholder="voce@exemplo.com"
                  type="email"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Senha</FormLabel>
              <FormControl>
                <SemanaInput autoComplete="current-password" type="password" {...field} />
              </FormControl>
              <Link
                className="text-sm underline underline-offset-4"
                href="/semana/reset-password"
              >
                Esqueci minha senha
              </Link>
              <FormMessage />
            </FormItem>
          )}
        />
        {error && <AuthNotice variant="error">{error}</AuthNotice>}
        {error && (
          <button
            className="text-sm font-medium underline underline-offset-4"
            disabled={resending}
            onClick={resend}
            type="button"
          >
            {resending ? 'Enviando…' : 'Reenviar verificação'}
          </button>
        )}
        {resendMessage && <AuthNotice>{resendMessage}</AuthNotice>}
        <SemanaButton
          className="w-full"
          disabled={form.formState.isSubmitting}
          type="submit"
        >
          {form.formState.isSubmitting ? 'Entrando…' : 'Entrar'}
        </SemanaButton>
      </form>
    </Form>
  )
}
