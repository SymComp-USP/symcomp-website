'use client'

import { useState } from 'react'
import { Check, Plus } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

import {
  createAdminAtividade,
  uploadAdminPalestrantePhoto,
  updateAdminAtividade,
  type AdminAtividade,
} from '../api'

type ActivityFormSpeaker = {
  nome: string
  sobre: string
  foto: File | null
  fotoUrl?: string
}

type ActivityFormState = {
  tipo: AdminAtividade['tipo']
  titulo: string
  descricao: string
  local: string
  palestrantes: ActivityFormSpeaker[]
  link_live: string
  comeca_as: string
  termina_as: string
  status: AdminAtividade['status']
  pontos: number
  horas: number
}

function localDateTime(value: string) {
  const date = new Date(value)
  const pad = (part: number) => String(part).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}

function activityFormState(atividade?: AdminAtividade): ActivityFormState {
  return {
    tipo: atividade?.tipo ?? 'palestra',
    titulo: atividade?.titulo ?? '',
    descricao: atividade?.descricao ?? '',
    local: atividade?.local ?? '',
    palestrantes: atividade?.palestrantes.length
      ? atividade.palestrantes.map((speaker) => ({
          nome: speaker.nome,
          sobre: speaker.sobre ?? '',
          foto: null,
          fotoUrl: speaker.foto,
        }))
      : [{ nome: '', sobre: '', foto: null }],
    link_live: atividade?.link_live ?? '',
    comeca_as: atividade ? localDateTime(atividade.comeca_as) : '',
    termina_as: atividade ? localDateTime(atividade.termina_as) : '',
    status: atividade?.status ?? 'provisoria',
    pontos: atividade?.pontos ?? 0,
    horas: atividade?.horas ?? 1,
  }
}

export function ActivityForm({
  semanaId,
  atividade,
  onDone,
}: {
  semanaId: number
  atividade?: AdminAtividade
  onDone: () => void
}) {
  const [form, setForm] = useState(() => activityFormState(atividade))
  const [error, setError] = useState('')

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    setError('')
    try {
      const speakers = form.palestrantes.filter((speaker) => speaker.nome.trim())
      const input = {
        tipo: form.tipo,
        titulo: form.titulo,
        descricao: form.descricao || null,
        local: form.local || null,
        palestrantes: speakers.map(({ nome, sobre, fotoUrl }) => ({
          nome,
          sobre,
          ...(fotoUrl ? { foto: fotoUrl } : {}),
        })),
        link_live: form.link_live || null,
        status: form.status,
        pontos: form.pontos,
        horas: form.horas,
        comeca_as: new Date(form.comeca_as).toISOString(),
        termina_as: new Date(form.termina_as).toISOString(),
      }
      const saved = atividade
        ? await updateAdminAtividade(semanaId, atividade.id, input)
        : await createAdminAtividade(semanaId, input)
      for (const [index, speaker] of speakers.entries()) {
        if (speaker.foto) {
          await uploadAdminPalestrantePhoto(semanaId, saved.id, index, speaker.foto)
        }
      }
      onDone()
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : 'Não foi possível criar a atividade.',
      )
    }
  }

  return (
    <form
      className="mt-4 grid gap-3 rounded-lg border border-indigo-100 bg-indigo-50 p-4 sm:grid-cols-2"
      onSubmit={submit}
    >
      <Input
        className="sm:col-span-2"
        placeholder="Título"
        required
        value={form.titulo}
        onChange={(event) => setForm({ ...form, titulo: event.target.value })}
      />
      <textarea
        className="min-h-24 rounded-md border border-input bg-background px-3 py-2 text-sm sm:col-span-2"
        placeholder="Descrição"
        value={form.descricao}
        onChange={(event) => setForm({ ...form, descricao: event.target.value })}
      />
      <Input
        placeholder="Local"
        value={form.local}
        onChange={(event) => setForm({ ...form, local: event.target.value })}
      />
      <Input
        placeholder="Link da transmissão"
        type="url"
        value={form.link_live}
        onChange={(event) => setForm({ ...form, link_live: event.target.value })}
      />
      <div className="space-y-3 sm:col-span-2">
        <div className="flex items-center justify-between">
          <p className="text-sm font-semibold">Palestrantes</p>
          <Button
            onClick={() =>
              setForm({
                ...form,
                palestrantes: [...form.palestrantes, { nome: '', sobre: '', foto: null }],
              })
            }
            size="sm"
            type="button"
            variant="outline"
          >
            <Plus size={14} /> Adicionar
          </Button>
        </div>
        {form.palestrantes.map((speaker, index) => (
          <div
            className="grid gap-2 rounded-md border border-indigo-100 bg-white p-3 sm:grid-cols-2"
            key={index}
          >
            <Input
              placeholder="Nome"
              value={speaker.nome}
              onChange={(event) => {
                const palestrantes = [...form.palestrantes]
                palestrantes[index] = { ...speaker, nome: event.target.value }
                setForm({ ...form, palestrantes })
              }}
            />
            <Input
              accept="image/jpeg,image/png,image/webp"
              type="file"
              onChange={(event) => {
                const palestrantes = [...form.palestrantes]
                palestrantes[index] = {
                  ...speaker,
                  foto: event.target.files?.[0] ?? null,
                }
                setForm({ ...form, palestrantes })
              }}
            />
            <textarea
              className="min-h-20 rounded-md border border-input bg-background px-3 py-2 text-sm sm:col-span-2"
              placeholder="Sobre o palestrante"
              value={speaker.sobre}
              onChange={(event) => {
                const palestrantes = [...form.palestrantes]
                palestrantes[index] = { ...speaker, sobre: event.target.value }
                setForm({ ...form, palestrantes })
              }}
            />
            {form.palestrantes.length > 1 && (
              <Button
                className="sm:col-span-2"
                onClick={() =>
                  setForm({
                    ...form,
                    palestrantes: form.palestrantes.filter((_, item) => item !== index),
                  })
                }
                type="button"
                variant="ghost"
              >
                Remover palestrante
              </Button>
            )}
          </div>
        ))}
      </div>
      <select
        className="h-10 rounded-md border border-input bg-background px-3 text-sm"
        value={form.tipo}
        onChange={(event) =>
          setForm({ ...form, tipo: event.target.value as AdminAtividade['tipo'] })
        }
      >
        <option value="palestra">Palestra</option>
        <option value="workshop">Workshop</option>
        <option value="conversa">Conversa</option>
        <option value="encerramento">Encerramento</option>
        <option value="coffee_break">Coffee break</option>
      </select>
      <select
        className="h-10 rounded-md border border-input bg-background px-3 text-sm"
        value={form.status}
        onChange={(event) =>
          setForm({ ...form, status: event.target.value as AdminAtividade['status'] })
        }
      >
        <option value="provisoria">Provisória</option>
        <option value="confirmada">Confirmada</option>
      </select>
      <label className="text-sm">
        Início
        <Input
          className="mt-1"
          required
          type="datetime-local"
          value={form.comeca_as}
          onChange={(event) => setForm({ ...form, comeca_as: event.target.value })}
        />
      </label>
      <label className="text-sm">
        Fim
        <Input
          className="mt-1"
          required
          type="datetime-local"
          value={form.termina_as}
          onChange={(event) => setForm({ ...form, termina_as: event.target.value })}
        />
      </label>
      <label className="text-sm">
        Pontos
        <Input
          className="mt-1"
          min={0}
          type="number"
          value={form.pontos}
          onChange={(event) => setForm({ ...form, pontos: Number(event.target.value) })}
        />
      </label>
      <label className="text-sm">
        Horas
        <Input
          className="mt-1"
          min={1}
          type="number"
          value={form.horas}
          onChange={(event) => setForm({ ...form, horas: Number(event.target.value) })}
        />
      </label>
      {error && <p className="text-sm text-red-700 sm:col-span-2">{error}</p>}
      <Button className="sm:col-span-2" type="submit">
        <Check size={16} /> {atividade ? 'Salvar alterações' : 'Criar atividade'}
      </Button>
    </form>
  )
}
