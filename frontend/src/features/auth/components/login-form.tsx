'use client'

import { zodResolver } from '@hookform/resolvers/zod'
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
import { SemanaButton } from '@/features/semana/components/semana-button'
import { SemanaInput } from '@/features/semana/components/semana-input'
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
    try {
      const user = await login(values)
      router.push(user?.isAdmin ? '/admin' : '/semana/perfil')
    } catch {
      setError('Não foi possível entrar. Tente novamente.')
    }
  }

  return (
    <Form {...form}>
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
              <FormMessage />
            </FormItem>
          )}
        />
        {error && (
          <p className="text-sm text-destructive" role="alert">
            {error}
          </p>
        )}
        <SemanaButton
          className="w-full"
          disabled={form.formState.isSubmitting}
          type="submit"
        >
          {form.formState.isSubmitting ? 'Entrando…' : 'Entrar'}
        </SemanaButton>
      </form>
      <div className="mt-5">
        <OAuthButtons />
      </div>
    </Form>
  )
}
