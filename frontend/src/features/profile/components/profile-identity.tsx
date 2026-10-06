'use client'

import { zodResolver } from '@hookform/resolvers/zod'
import { CheckCircle2, Mail, Pencil } from 'lucide-react'
import { useState } from 'react'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/features/auth/auth-provider'
import { AuthNotice } from '@/features/auth/components/auth-notice'
import type { User } from '@/features/auth/types'
import { SemanaButton } from '@/features/semana/components/semana-button'
import { SemanaInput } from '@/features/semana/components/semana-input'

// Same rules as the backend: required after trimming, at most 255 characters.
const schema = z.object({
  name: z
    .string()
    .trim()
    .min(1, 'Digite seu nome completo.')
    .max(255, 'O nome deve ter no máximo 255 caracteres.'),
})

type Values = z.infer<typeof schema>

function initials(name: string) {
  return name
    .split(' ')
    .slice(0, 2)
    .map((part) => part[0])
    .join('')
    .toUpperCase()
}

export function ProfileIdentity({ user }: { user: User }) {
  const { updateName } = useAuth()
  const [editing, setEditing] = useState(false)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<string>()
  const form = useForm<Values>({
    resolver: zodResolver(schema),
    defaultValues: { name: user.name },
  })

  function startEditing() {
    form.reset({ name: user.name })
    setError(undefined)
    setSaved(false)
    setEditing(true)
  }

  function cancelEditing() {
    setError(undefined)
    setEditing(false)
  }

  async function submit(values: Values) {
    setError(undefined)

    if (values.name === user.name) {
      setEditing(false)
      return
    }

    try {
      await updateName(values.name)
      setSaved(true)
      setEditing(false)
    } catch {
      setError('Não foi possível salvar seu nome. Tente novamente.')
    }
  }

  return (
    <section className="rounded-none border-[8px] border-white bg-card p-6 text-card-foreground shadow-[0_10px_0_hsl(var(--semana-contrast))] sm:p-8">
      <div className="flex flex-col gap-5 sm:flex-row sm:items-center">
        <Avatar className="h-20 w-20">
          <AvatarFallback className="text-xl font-semibold">
            {initials(user.name)}
          </AvatarFallback>
        </Avatar>
        <div className="min-w-0 flex-1">
          <h2 className="break-words text-2xl font-semibold">{user.name}</h2>
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

      {editing ? (
        <Form {...form}>
          <form
            className="mt-6 space-y-5 border-t pt-6"
            onSubmit={form.handleSubmit(submit)}
          >
            <AuthNotice>Use seu nome completo, como no documento.</AuthNotice>
            <FormField
              control={form.control}
              name="name"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Nome completo</FormLabel>
                  <FormControl>
                    <SemanaInput
                      autoComplete="name"
                      autoFocus
                      placeholder="Nome e sobrenome"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <div className="space-y-2">
              <Label htmlFor="profile-email">E-mail</Label>
              <SemanaInput
                aria-describedby="profile-email-hint"
                aria-readonly="true"
                className="cursor-not-allowed bg-muted"
                id="profile-email"
                readOnly
                value={user.email}
              />
              <p className="text-sm text-muted-foreground" id="profile-email-hint">
                O e-mail não pode ser alterado.
              </p>
            </div>
            {error && (
              <p className="text-sm text-destructive" role="alert">
                {error}
              </p>
            )}
            <div className="flex flex-wrap items-center gap-3">
              <SemanaButton disabled={form.formState.isSubmitting} type="submit">
                {form.formState.isSubmitting ? 'Salvando…' : 'Salvar'}
              </SemanaButton>
              <Button
                disabled={form.formState.isSubmitting}
                onClick={cancelEditing}
                type="button"
                variant="outline"
              >
                Cancelar
              </Button>
            </div>
          </form>
        </Form>
      ) : (
        <div className="mt-6 flex flex-wrap items-center gap-3 border-t pt-6">
          <Button onClick={startEditing} size="sm" type="button" variant="outline">
            <Pencil aria-hidden="true" className="mr-2" size={14} />
            Editar nome
          </Button>
          <p
            aria-live="polite"
            className="inline-flex items-center gap-2 text-sm font-medium"
            role="status"
          >
            {saved && (
              <>
                <CheckCircle2 aria-hidden="true" size={16} /> Nome atualizado.
              </>
            )}
          </p>
        </div>
      )}
    </section>
  )
}
