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
import { AuthNotice } from './auth-notice'
import { OAuthButtons } from './oauth-buttons'

const schema = z.object({
  name: z.string().trim().min(1, 'Digite seu nome.').max(255),
  email: z.string().email('Digite um e-mail válido.'),
  password: z.string().min(8, 'A senha deve ter pelo menos 8 caracteres.'),
})

type Values = z.infer<typeof schema>

export function RegisterForm({ onSuccess }: { onSuccess: (message: string) => void }) {
  const router = useRouter()
  const { loading, register, user } = useAuth()
  const [error, setError] = useState<string>()
  const form = useForm<Values>({
    resolver: zodResolver(schema),
    defaultValues: { name: '', email: '', password: '' },
  })

  useEffect(() => {
    if (!loading && user) router.replace('/semana/perfil')
  }, [loading, router, user])

  if (loading || user) {
    return <p>{user ? 'Você já está conectado.' : 'Carregando…'}</p>
  }

  async function submit(values: Values) {
    setError(undefined)
    try {
      await register(values)
      onSuccess('Conta criada. Verifique seu e-mail para ativar o acesso.')
      form.reset()
    } catch {
      setError('Não foi possível criar sua conta. Tente novamente.')
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
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Nome</FormLabel>
              <FormControl>
                <SemanaInput autoComplete="name" placeholder="Seu nome" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
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
                <SemanaInput autoComplete="new-password" type="password" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        {error && <AuthNotice variant="error">{error}</AuthNotice>}
        <SemanaButton
          className="w-full"
          disabled={form.formState.isSubmitting}
          type="submit"
        >
          {form.formState.isSubmitting ? 'Criando conta…' : 'Criar conta'}
        </SemanaButton>
      </form>
    </Form>
  )
}
