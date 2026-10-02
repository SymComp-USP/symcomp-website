'use client'

import { useEffect, useState } from 'react'
import { Minus, Plus } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

import {
  adjustAdminChallengeParticipantScore,
  listAdminChallengeParticipants,
  type AdminChallenge,
  type AdminChallengeParticipant,
} from '../api'

const PAGE_SIZE = 50

type ParticipantPage = {
  items: AdminChallengeParticipant[]
  total: number
  limit: number
  offset: number
}

export function PointsSection({ challenges }: { challenges: AdminChallenge[] }) {
  const [page, setPage] = useState<ParticipantPage>()
  const [offset, setOffset] = useState(0)
  const [refresh, setRefresh] = useState(0)
  const [challengeId, setChallengeId] = useState('')
  const [participantQuery, setParticipantQuery] = useState('')
  const [pendingId, setPendingId] = useState<string>()
  const [amounts, setAmounts] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    setLoading(true)
    setError('')
    listAdminChallengeParticipants(PAGE_SIZE, offset, challengeId, participantQuery)
      .then((result) => {
        if (active) setPage(result)
      })
      .catch((reason: Error) => {
        if (active) setError(reason.message)
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [challengeId, offset, participantQuery, refresh])

  function updateFilters(nextChallengeId: string, nextParticipantQuery: string) {
    setChallengeId(nextChallengeId)
    setParticipantQuery(nextParticipantQuery)
    setOffset(0)
  }

  async function adjustScore(participant: AdminChallengeParticipant, direction: 1 | -1) {
    const amount = Number(amounts[participant.id] ?? '1')
    if (!Number.isSafeInteger(amount) || amount < 1) {
      setError('Informe uma quantidade de pontos maior que zero.')
      return
    }

    setPendingId(participant.id)
    setError('')
    try {
      const updatedParticipant = await adjustAdminChallengeParticipantScore(
        participant.challenge_id,
        participant.id,
        amount * direction,
      )
      setPage((current) =>
        current
          ? {
              ...current,
              items: current.items.map((item) =>
                item.id === updatedParticipant.id
                  ? { ...item, score: updatedParticipant.score }
                  : item,
              ),
            }
          : current,
      )
      setRefresh((value) => value + 1)
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : 'Não foi possível ajustar os pontos.',
      )
    } finally {
      setPendingId(undefined)
    }
  }

  const items = page?.items ?? []
  const firstItem = page && page.total > 0 ? page.offset + 1 : 0
  const lastItem = page ? page.offset + items.length : 0

  return (
    <section>
      <div className="flex items-center justify-between gap-4">
        <p className="text-sm text-slate-500">
          Ajuste manual de pontos por participante e desafio.
        </p>
        {loading && <span className="text-xs text-slate-500">Carregando…</span>}
      </div>
      {error && (
        <p className="mt-3 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </p>
      )}
      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        <select
          aria-label="Filtrar por desafio"
          className="h-10 rounded-md border border-input bg-background px-3 text-sm"
          value={challengeId}
          onChange={(event) => updateFilters(event.target.value, participantQuery)}
        >
          <option value="">Todos os desafios</option>
          {challenges.map((challenge) => (
            <option key={challenge.id} value={challenge.id}>
              {challenge.title}
            </option>
          ))}
        </select>
        <Input
          aria-label="Filtrar por participante"
          placeholder="Nome ou e-mail do participante"
          type="search"
          value={participantQuery}
          onChange={(event) => updateFilters(challengeId, event.target.value)}
        />
      </div>
      <div className="mt-5 overflow-x-auto rounded-lg border border-slate-200 bg-white">
        <table className="w-full min-w-[680px] text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th className="p-4">Desafio</th>
              <th className="p-4">Participante</th>
              <th className="p-4 text-right">Pontos</th>
              <th className="p-4 text-right">Ajuste</th>
            </tr>
          </thead>
          <tbody>
            {items.map((participant) => {
              const amount = Number(amounts[participant.id] ?? '1')
              const canAdjust = Number.isSafeInteger(amount) && amount > 0
              const pending = pendingId === participant.id

              return (
                <tr
                  className="border-b border-slate-100 last:border-0"
                  key={participant.id}
                >
                  <td className="p-4 font-semibold">{participant.challenge_title}</td>
                  <td className="p-4">
                    <p className="font-medium">{participant.user_name}</p>
                    <p className="text-xs text-slate-500">{participant.user_email}</p>
                  </td>
                  <td className="p-4 text-right font-semibold tabular-nums">
                    {participant.score}
                  </td>
                  <td className="p-4">
                    <div className="flex items-center justify-end gap-2">
                      <Input
                        aria-label={`Quantidade de pontos para ${participant.user_name}`}
                        className="h-9 w-24"
                        min={1}
                        step={1}
                        type="number"
                        value={amounts[participant.id] ?? '1'}
                        onChange={(event) =>
                          setAmounts((current) => ({
                            ...current,
                            [participant.id]: event.target.value,
                          }))
                        }
                      />
                      <Button
                        aria-label={`Adicionar pontos a ${participant.user_name}`}
                        disabled={pending || !canAdjust}
                        onClick={() => adjustScore(participant, 1)}
                        size="icon"
                        title="Adicionar pontos"
                        type="button"
                        variant="outline"
                      >
                        <Plus size={16} />
                      </Button>
                      <Button
                        aria-label={`Remover pontos de ${participant.user_name}`}
                        disabled={pending || !canAdjust}
                        onClick={() => adjustScore(participant, -1)}
                        size="icon"
                        title="Remover pontos"
                        type="button"
                        variant="outline"
                      >
                        <Minus size={16} />
                      </Button>
                    </div>
                  </td>
                </tr>
              )
            })}
            {!items.length && !loading && (
              <tr>
                <td className="p-6 text-center text-slate-500" colSpan={4}>
                  Nenhum participante encontrado.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
      <div className="mt-4 flex items-center justify-between gap-4 text-sm">
        <p className="text-slate-500">
          Mostrando {firstItem}–{lastItem} de {page?.total ?? 0}
        </p>
        <div className="flex gap-2">
          <Button
            disabled={offset === 0 || loading}
            onClick={() => setOffset((value) => Math.max(0, value - PAGE_SIZE))}
            type="button"
            variant="outline"
          >
            Anterior
          </Button>
          <Button
            disabled={!page || lastItem >= page.total || loading}
            onClick={() => setOffset((value) => value + PAGE_SIZE)}
            type="button"
            variant="outline"
          >
            Próxima
          </Button>
        </div>
      </div>
    </section>
  )
}
