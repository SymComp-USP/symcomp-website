'use client'

import { useEffect, useState } from 'react'
import { Trash2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

import {
  createAdminPresenca,
  regenerateAdminAtividadeCode,
  type AdminAtividade,
  type AdminPresenca,
} from '../api'

import { ActivityForm } from './activity-form'

export function ActivityCodeAction({
  atividade,
  semanaId,
  onChanged,
  onError,
}: {
  atividade: AdminAtividade
  semanaId: number
  onChanged: () => void
  onError: (message: string) => void
}) {
  const [code, setCode] = useState(atividade.codigo)

  useEffect(() => {
    setCode(atividade.codigo)
  }, [atividade.codigo])

  async function regenerate() {
    if (!window.confirm('O código anterior deixará de funcionar. Continuar?')) return
    try {
      const updated = await regenerateAdminAtividadeCode(semanaId, atividade.id)
      setCode(updated.codigo)
      onChanged()
    } catch (reason) {
      onError(
        reason instanceof Error ? reason.message : 'Não foi possível regenerar o código.',
      )
    }
  }

  return (
    <div className="mt-4 flex items-center justify-between rounded-md bg-slate-50 p-3">
      <div>
        <p className="text-xs uppercase tracking-wider text-slate-500">Código</p>
        <p className="font-mono text-2xl font-bold tracking-[0.3em]">{code}</p>
      </div>
      <Button onClick={regenerate} size="sm" type="button" variant="outline">
        Regenerar código
      </Button>
    </div>
  )
}

export function ActivityCard({
  atividade,
  semanaId,
  onChanged,
  onError,
  onDelete,
}: {
  atividade: AdminAtividade
  semanaId: number
  onChanged: () => void
  onError: (message: string) => void
  onDelete: () => void
}) {
  const [editing, setEditing] = useState(false)

  return (
    <article className="rounded-lg border border-slate-200 bg-slate-50 p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-xs font-bold uppercase tracking-wider text-indigo-600">
            {atividade.tipo} · {atividade.status}
          </p>
          <h4 className="mt-1 font-semibold">{atividade.titulo || 'Sem título'}</h4>
          <p className="mt-1 text-xs text-slate-500">
            {new Date(atividade.comeca_as).toLocaleString('pt-BR')} · {atividade.horas}h ·{' '}
            {atividade.pontos} pontos
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            onClick={() => setEditing((value) => !value)}
            size="sm"
            type="button"
            variant="outline"
          >
            {editing ? 'Cancelar' : 'Editar'}
          </Button>
          <button
            aria-label={`Remover ${atividade.titulo || 'atividade'}`}
            className="text-slate-400 hover:text-red-600"
            onClick={onDelete}
            type="button"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>
      {editing && (
        <ActivityForm
          atividade={atividade}
          onDone={() => {
            setEditing(false)
            onChanged()
          }}
          semanaId={semanaId}
        />
      )}
      <ActivityCodeAction
        key={atividade.id}
        atividade={atividade}
        onChanged={onChanged}
        onError={onError}
        semanaId={semanaId}
      />
      <ManualPresenceForm
        atividadeId={atividade.id}
        onDone={onChanged}
        semanaId={semanaId}
      />
    </article>
  )
}

export function ManualPresenceForm({
  semanaId,
  atividadeId,
  onDone,
}: {
  semanaId: number
  atividadeId: string
  onDone: (presenca: AdminPresenca) => void
}) {
  const [open, setOpen] = useState(false)
  const [form, setForm] = useState({ nome: '', email: '' })
  const [error, setError] = useState('')

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    setError('')
    try {
      const presenca = await createAdminPresenca(semanaId, atividadeId, form)
      setForm({ nome: '', email: '' })
      setOpen(false)
      onDone(presenca)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Não foi possível registrar.')
    }
  }

  if (!open) {
    return (
      <Button
        className="mt-3 w-full"
        onClick={() => setOpen(true)}
        type="button"
        variant="ghost"
      >
        Registrar presença manual
      </Button>
    )
  }

  return (
    <form
      className="mt-3 space-y-2 rounded-md border border-amber-200 bg-amber-50 p-3"
      onSubmit={submit}
    >
      <p className="text-xs font-semibold text-amber-900">Presença manual</p>
      <Input
        placeholder="Nome"
        value={form.nome}
        onChange={(event) => setForm({ ...form, nome: event.target.value })}
      />
      <p className="text-xs text-amber-800">
        Para usuário cadastrado, e-mail basta. Visitante precisa de nome.
      </p>
      <Input
        placeholder="E-mail"
        required
        type="email"
        value={form.email}
        onChange={(event) => setForm({ ...form, email: event.target.value })}
      />
      {error && <p className="text-xs text-red-700">{error}</p>}
      <div className="flex gap-2">
        <Button type="submit">Registrar</Button>
        <Button onClick={() => setOpen(false)} type="button" variant="outline">
          Cancelar
        </Button>
      </div>
    </form>
  )
}
