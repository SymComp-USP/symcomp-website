'use client'

import { useEffect, useState } from 'react'
import { Trash2 } from 'lucide-react'

import {
  deleteAdminPresenca,
  listAdminPresencas,
  type AdminAtividade,
  type AdminPresenca,
  type AdminSemana,
} from '../api'

import { ActivityCodeAction, ManualPresenceForm } from './activity-presence'

export function ActivitiesSection({
  atividades,
  semanas,
}: {
  atividades: Record<number, AdminAtividade[]>
  semanas: AdminSemana[]
}) {
  const allActivities = semanas.flatMap((semana) =>
    (atividades[semana.id] ?? []).map((atividade) => ({ atividade, semana })),
  )
  const [selectedId, setSelectedId] = useState<string>()
  const [presencas, setPresencas] = useState<AdminPresenca[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [refresh, setRefresh] = useState(0)
  const selected = allActivities.find(({ atividade }) => atividade.id === selectedId)
  const selectedSemanaId = selected?.semana.id

  useEffect(() => {
    if (!selectedId || selectedSemanaId === undefined) {
      setPresencas([])
      return
    }
    setLoading(true)
    listAdminPresencas(selectedSemanaId, selectedId)
      .then(setPresencas)
      .catch((reason: Error) => setError(reason.message))
      .finally(() => setLoading(false))
  }, [refresh, selectedId, selectedSemanaId])

  async function removePresence(presenca: AdminPresenca) {
    if (!selected || !window.confirm(`Remover presença de ${presenca.nome}?`)) return
    try {
      await deleteAdminPresenca(selected.semana.id, selected.atividade.id, presenca.id)
      setRefresh((value) => value + 1)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Não foi possível remover.')
    }
  }

  return (
    <section>
      <p className="text-sm text-slate-500">
        Todas atividades cadastradas. Selecione uma para administrar código e presenças.
      </p>
      {error && <p className="mt-3 text-sm text-red-700">{error}</p>}
      <div className="mt-5 grid gap-5 lg:grid-cols-[minmax(0,1fr)_minmax(0,1.4fr)]">
        <div className="space-y-3">
          {allActivities.map(({ atividade, semana }) => (
            <button
              className={`w-full rounded-xl border p-4 text-left ${selectedId === atividade.id ? 'border-slate-950 bg-slate-950 text-white' : 'border-slate-200 bg-white hover:border-slate-400'}`}
              key={atividade.id}
              onClick={() => setSelectedId(atividade.id)}
              type="button"
            >
              <p className="text-xs font-bold uppercase tracking-wider opacity-70">
                {semana.nome} · {semana.ano}
              </p>
              <p className="mt-1 font-bold">{atividade.titulo || 'Sem título'}</p>
              <p className="mt-1 text-xs opacity-70">
                {new Date(atividade.comeca_as).toLocaleString('pt-BR')} ·{' '}
                {atividade.status}
              </p>
            </button>
          ))}
          {!allActivities.length && (
            <p className="rounded-xl border border-dashed border-slate-300 p-5 text-sm text-slate-500">
              Nenhuma atividade cadastrada.
            </p>
          )}
        </div>

        {selected ? (
          <div className="rounded-xl border border-slate-200 bg-white p-5">
            <p className="text-xs font-bold uppercase tracking-wider text-indigo-600">
              {selected.semana.nome} · {selected.semana.ano}
            </p>
            <h2 className="mt-1 text-xl font-bold">
              {selected.atividade.titulo || 'Sem título'}
            </h2>
            <ActivityCodeAction
              atividade={selected.atividade}
              onChanged={() => setRefresh((value) => value + 1)}
              onError={setError}
              semanaId={selected.semana.id}
            />
            <div className="mt-6 flex items-center justify-between">
              <h3 className="font-bold">Presenças ({presencas.length})</h3>
              {loading && <span className="text-xs text-slate-500">Carregando…</span>}
            </div>
            <div className="mt-3 space-y-2">
              {presencas.map((presenca) => (
                <div
                  className="flex items-center justify-between gap-3 rounded-md border border-slate-100 p-3 text-sm"
                  key={presenca.id}
                >
                  <div>
                    <p className="font-semibold">{presenca.nome}</p>
                    <p className="text-xs text-slate-500">
                      {presenca.email} · {presenca.horas}h
                    </p>
                  </div>
                  <button
                    aria-label={`Remover presença de ${presenca.nome}`}
                    className="text-slate-400 hover:text-red-600"
                    onClick={() => removePresence(presenca)}
                    type="button"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              ))}
              {!presencas.length && !loading && (
                <p className="text-sm text-slate-500">Nenhuma presença registrada.</p>
              )}
            </div>
            <ManualPresenceForm
              atividadeId={selected.atividade.id}
              onDone={() => setRefresh((value) => value + 1)}
              semanaId={selected.semana.id}
            />
          </div>
        ) : (
          <div className="flex min-h-48 items-center justify-center rounded-xl border border-dashed border-slate-300 p-5 text-sm text-slate-500">
            Selecione uma atividade.
          </div>
        )}
      </div>
    </section>
  )
}
