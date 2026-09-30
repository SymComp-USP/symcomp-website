import { requestApi } from '@/features/auth/api'

export type Semana = {
  id: number
  nome: string
  ano: number
}

export type SemanaRankingEntry = {
  participant_id: string
  nickname: string
  points: number
}

export function listSemanas() {
  return requestApi<Semana[]>('/semanas')
}

export function getSemanaRanking(semanaId: number) {
  return requestApi<SemanaRankingEntry[]>(`/semanas/${semanaId}/ranking`)
}

export function registerAttendance(
  semanaId: number,
  codigo: string,
  input: { nome?: string; email?: string },
) {
  return requestApi<{
    atividade_id: string
    registrada: boolean
    pontos_adicionados: number
    horas: number
  }>(`/semanas/${semanaId}/atividades/registrar/${codigo}`, {
    method: 'POST',
    body: JSON.stringify(input),
  })
}
