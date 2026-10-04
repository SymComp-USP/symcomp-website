'use client'

import { useState } from 'react'
import { Plus, Trash2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

import {
  createAdminSemana,
  deleteAdminAtividade,
  deleteAdminSemana,
  updateAdminSemana,
  type AdminAtividade,
  type AdminSemana,
} from '../api'

import { ActivityForm } from './activity-form'
import { ActivityCard } from './activity-presence'

export function SemanasSection({
  atividades,
  semanas,
  onActivitySaved,
  onActivityDeleted,
  onActivityChanged,
  onChanged,
}: {
  atividades: Record<number, AdminAtividade[]>
  semanas: AdminSemana[]
  onActivitySaved: (atividade: AdminAtividade) => void
  onActivityDeleted: (semanaId: number, atividadeId: string) => void
  onActivityChanged: () => void
  onChanged: () => void
}) {
  const [form, setForm] = useState({ nome: '', ano: new Date().getFullYear() })
  const [error, setError] = useState('')
  const [openActivityForm, setOpenActivityForm] = useState<number>()

  async function create(event: React.FormEvent) {
    event.preventDefault()
    try {
      await createAdminSemana(form)
      setForm({ nome: '', ano: new Date().getFullYear() })
      onChanged()
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : 'Não foi possível criar a Semana.',
      )
    }
  }

  async function rename(semana: AdminSemana) {
    const nome = window.prompt('Nome da Semana', semana.nome)
    if (!nome || nome === semana.nome) return
    try {
      await updateAdminSemana(semana.id, { nome })
      onChanged()
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : 'Não foi possível atualizar a Semana.',
      )
    }
  }

  async function remove(semana: AdminSemana) {
    if (semana.challenge_count || semana.participant_count) {
      setError('Uma Semana com desafios ou participantes não pode ser removida.')
      return
    }
    if (!window.confirm(`Remover ${semana.nome}?`)) return
    try {
      await deleteAdminSemana(semana.id)
      onChanged()
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : 'Não foi possível remover a Semana.',
      )
    }
  }

  return (
    <section>
      <p className="text-sm text-slate-500">
        Uma Semana pode conter vários desafios; os desafios podem ser associados pelo seu
        `semana_id`.
      </p>
      <form
        className="mt-5 grid gap-3 rounded-xl border border-indigo-100 bg-indigo-50 p-5 sm:grid-cols-[1fr_140px_auto]"
        onSubmit={create}
      >
        <Input
          required
          placeholder="Nome da Semana"
          value={form.nome}
          onChange={(event) => setForm({ ...form, nome: event.target.value })}
        />
        <Input
          required
          type="number"
          value={form.ano}
          onChange={(event) => setForm({ ...form, ano: Number(event.target.value) })}
        />
        <Button type="submit">
          <Plus size={16} /> Criar Semana
        </Button>
      </form>
      {error && <p className="mt-3 text-sm text-red-700">{error}</p>}
      <div className="mt-5 grid gap-4 md:grid-cols-2">
        {semanas.map((semana) => (
          <article
            className="rounded-xl border border-slate-200 bg-white p-5"
            key={semana.id}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-indigo-600">
                  {semana.ano}
                </p>
                <h2 className="mt-1 font-bold">{semana.nome}</h2>
              </div>
              <div className="flex gap-3">
                <button
                  className="text-sm font-semibold text-indigo-600"
                  onClick={() => rename(semana)}
                >
                  Editar
                </button>
                <button
                  aria-label={`Remover ${semana.nome}`}
                  className="text-slate-400 hover:text-red-600"
                  onClick={() => remove(semana)}
                >
                  <Trash2 size={17} />
                </button>
              </div>
            </div>
            <p className="mt-4 text-sm text-slate-500">
              {semana.challenge_count} desafios · {semana.participant_count} participantes
            </p>
            <div className="mt-5 border-t border-slate-100 pt-5">
              <div className="flex items-center justify-between gap-3">
                <h3 className="text-sm font-bold">Atividades</h3>
                <Button
                  onClick={() => setOpenActivityForm(semana.id)}
                  size="sm"
                  type="button"
                >
                  <Plus size={14} /> Nova atividade
                </Button>
              </div>
              {openActivityForm === semana.id && (
                <ActivityForm
                  onDone={(atividade) => {
                    setOpenActivityForm(undefined)
                    onActivitySaved(atividade)
                  }}
                  semanaId={semana.id}
                />
              )}
              <div className="mt-4 space-y-3">
                {(atividades[semana.id] ?? []).map((atividade) => (
                  <ActivityCard
                    atividade={atividade}
                    key={atividade.id}
                    onActivitySaved={onActivitySaved}
                    onChanged={onActivityChanged}
                    onError={setError}
                    onDelete={async () => {
                      if (
                        !window.confirm(
                          `Remover ${atividade.titulo || 'esta atividade'}?`,
                        )
                      )
                        return
                      try {
                        await deleteAdminAtividade(semana.id, atividade.id)
                        onActivityDeleted(semana.id, atividade.id)
                      } catch (reason) {
                        setError(
                          reason instanceof Error
                            ? reason.message
                            : 'Não foi possível remover a atividade.',
                        )
                      }
                    }}
                    semanaId={semana.id}
                  />
                ))}
                {!atividades[semana.id]?.length && (
                  <p className="text-sm text-slate-500">Nenhuma atividade cadastrada.</p>
                )}
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
