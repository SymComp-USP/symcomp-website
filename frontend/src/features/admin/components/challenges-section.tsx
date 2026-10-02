'use client'

import { useEffect, useState } from 'react'
import { Check, Pencil, Plus, Trash2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

import {
  createAdminChallenge,
  updateAdminChallenge,
  uploadAdminChallengeImage,
  type AdminChallenge,
  type AdminSemana,
} from '../api'

export function ChallengesSection({
  challenges,
  semanas,
  onSaved,
  onDelete,
}: {
  challenges: AdminChallenge[]
  semanas: AdminSemana[]
  onSaved: (challenge: AdminChallenge) => void
  onDelete: (id: string) => void
}) {
  const [open, setOpen] = useState(false)
  const [editingChallenge, setEditingChallenge] = useState<AdminChallenge | null>(null)
  return (
    <section>
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">Desafios e recompensas da Semana</p>
        <Button
          onClick={() => {
            setEditingChallenge(null)
            setOpen(true)
          }}
        >
          <Plus size={16} /> Novo desafio
        </Button>
      </div>
      {(open || editingChallenge) && (
        <ChallengeForm
          challenge={editingChallenge ?? undefined}
          key={editingChallenge?.id ?? 'new'}
          semanas={semanas}
          onDone={(savedChallenge) => {
            setOpen(false)
            setEditingChallenge(null)
            onSaved(savedChallenge)
          }}
        />
      )}
      <div className="mt-5 grid gap-4 md:grid-cols-2">
        {challenges.map((item) => (
          <article
            className="rounded-xl border border-slate-200 bg-white p-5"
            key={item.id}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-indigo-600">
                  {item.scoring_type}
                </p>
                <h2 className="mt-1 font-bold">{item.title}</h2>
              </div>
              <div className="flex items-center gap-3">
                <button
                  aria-label={`Editar ${item.title}`}
                  className="text-slate-400 hover:text-indigo-600"
                  onClick={() => {
                    setOpen(false)
                    setEditingChallenge(item)
                  }}
                >
                  <Pencil size={17} />
                </button>
                <button
                  aria-label={`Remover ${item.title}`}
                  className="text-slate-400 hover:text-red-600"
                  onClick={() => onDelete(item.id)}
                >
                  <Trash2 size={17} />
                </button>
              </div>
            </div>
            <p className="mt-4 text-sm text-slate-500">
              {item.points_value} pontos · encerra em{' '}
              {new Date(item.finishes_at).toLocaleDateString('pt-BR')}
            </p>
          </article>
        ))}
      </div>
    </section>
  )
}

function ChallengeForm({
  onDone,
  semanas,
  challenge,
}: {
  onDone: (challenge: AdminChallenge) => void
  semanas: AdminSemana[]
  challenge?: AdminChallenge
}) {
  const latestSemanaId = semanas
    .slice()
    .sort((a, b) => b.ano - a.ano || b.id - a.id)[0]
    ?.id.toString()
  const [form, setForm] = useState(() => ({
    title: challenge?.title ?? '',
    prompt: challenge?.prompt ?? '',
    scoring_type: challenge?.scoring_type ?? ('quiz' as const),
    finishes_at: challenge ? toDateTimeLocal(challenge.finishes_at) : '',
    points_value: challenge?.points_value ?? 10,
    input_answer: challenge?.input_answer ?? '',
    questions: challenge?.questions?.length
      ? challenge.questions.map(({ prompt, answer }) => ({ prompt, answer }))
      : [{ prompt: '', answer: '' }],
    semana_id: challenge?.semana_id?.toString() ?? latestSemanaId ?? '',
  }))
  const [image, setImage] = useState<File | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!latestSemanaId) return
    setForm((current) => ({
      ...current,
      semana_id: current.semana_id || latestSemanaId,
    }))
  }, [latestSemanaId])

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    try {
      const challengeInput = {
        title: form.title,
        scoring_type: form.scoring_type,
        finishes_at: new Date(form.finishes_at).toISOString(),
        semana_id: form.semana_id ? Number(form.semana_id) : undefined,
      }
      const scoringInput =
        form.scoring_type === 'input'
          ? {
              points_value: form.points_value,
              prompt: form.prompt,
              input_answer: form.input_answer,
            }
          : form.scoring_type === 'quiz'
            ? { points_value: form.points_value, questions: form.questions }
            : {}
      const input = {
        ...challengeInput,
        ...scoringInput,
      }
      const savedChallenge = challenge
        ? await updateAdminChallenge(challenge.id, input)
        : await createAdminChallenge(input)
      if (image) await uploadAdminChallengeImage(savedChallenge.id, image)
      onDone(savedChallenge)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Não foi possível criar.')
    }
  }

  return (
    <form
      className="my-5 grid gap-3 rounded-xl border border-indigo-100 bg-indigo-50 p-5 sm:grid-cols-2"
      onSubmit={submit}
    >
      <Input
        required
        placeholder="Título"
        value={form.title}
        onChange={(event) => setForm({ ...form, title: event.target.value })}
      />
      <select
        aria-label="Tipo de desafio"
        className="h-10 rounded-md border border-input bg-background px-3 text-sm"
        value={form.scoring_type}
        onChange={(event) =>
          setForm({
            ...form,
            scoring_type: event.target.value as AdminChallenge['scoring_type'],
          })
        }
      >
        <option value="quiz">Quiz</option>
        <option value="input">Resposta livre</option>
        <option value="manual">Manual</option>
      </select>
      <select
        className="h-10 rounded-md border border-input bg-background px-3 text-sm"
        value={form.semana_id}
        onChange={(event) => setForm({ ...form, semana_id: event.target.value })}
      >
        <option value="">Sem associar a uma Semana</option>
        {semanas.map((semana) => (
          <option key={semana.id} value={semana.id}>
            {semana.nome} ({semana.ano})
          </option>
        ))}
      </select>
      {form.scoring_type === 'input' && (
        <>
          <Input
            className="sm:col-span-2"
            placeholder="Enunciado"
            required
            value={form.prompt}
            onChange={(event) => setForm({ ...form, prompt: event.target.value })}
          />
          <Input
            className="sm:col-span-2"
            placeholder="Resposta esperada"
            required
            value={form.input_answer}
            onChange={(event) => setForm({ ...form, input_answer: event.target.value })}
          />
        </>
      )}
      {form.scoring_type === 'quiz' && (
        <div className="space-y-3 sm:col-span-2">
          <div className="flex items-center justify-between gap-3">
            <h3 className="text-sm font-semibold">Perguntas</h3>
            <Button
              onClick={() =>
                setForm({
                  ...form,
                  questions: [...form.questions, { prompt: '', answer: '' }],
                })
              }
              size="sm"
              type="button"
              variant="outline"
            >
              <Plus size={14} /> Adicionar pergunta
            </Button>
          </div>
          {form.questions.map((question, index) => (
            <div
              className="grid gap-2 rounded-md border border-indigo-100 bg-white p-3 sm:grid-cols-2"
              key={index}
            >
              <Input
                placeholder={`Pergunta ${index + 1}`}
                required
                value={question.prompt}
                onChange={(event) =>
                  setForm({
                    ...form,
                    questions: form.questions.map((item, itemIndex) =>
                      itemIndex === index
                        ? { ...item, prompt: event.target.value }
                        : item,
                    ),
                  })
                }
              />
              <Input
                placeholder={`Resposta correta ${index + 1}`}
                required
                value={question.answer}
                onChange={(event) =>
                  setForm({
                    ...form,
                    questions: form.questions.map((item, itemIndex) =>
                      itemIndex === index
                        ? { ...item, answer: event.target.value }
                        : item,
                    ),
                  })
                }
              />
              <Button
                aria-label={`Remover pergunta ${index + 1}`}
                className="sm:col-span-2 sm:justify-self-end"
                onClick={() =>
                  setForm({
                    ...form,
                    questions: form.questions.filter(
                      (_, itemIndex) => itemIndex !== index,
                    ),
                  })
                }
                size="sm"
                type="button"
                variant="ghost"
              >
                <Trash2 size={14} /> Remover
              </Button>
            </div>
          ))}
        </div>
      )}
      <label className="sm:col-span-2">
        <span className="mb-2 block text-sm font-medium">Imagem do desafio</span>
        <Input
          accept="image/*"
          type="file"
          onChange={(event) => setImage(event.target.files?.[0] ?? null)}
        />
      </label>
      <Input
        required
        type="datetime-local"
        value={form.finishes_at}
        onChange={(event) => setForm({ ...form, finishes_at: event.target.value })}
      />
      {form.scoring_type !== 'manual' && (
        <Input
          min={0}
          required
          type="number"
          value={form.points_value}
          onChange={(event) =>
            setForm({ ...form, points_value: Number(event.target.value) })
          }
        />
      )}
      {error && <p className="text-sm text-red-700">{error}</p>}
      <Button className="sm:col-span-2" type="submit">
        <Check size={16} /> {challenge ? 'Salvar alterações' : 'Criar desafio'}
      </Button>
    </form>
  )
}

function toDateTimeLocal(value: string) {
  const date = new Date(value)
  const pad = (part: number) => String(part).padStart(2, '0')
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
}
