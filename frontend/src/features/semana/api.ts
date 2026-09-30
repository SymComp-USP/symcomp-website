import { requestApi } from '@/features/auth/api'

export type SemanaEvent = {
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
  return requestApi<SemanaEvent[]>('/semana/')
}

export function getSemanaRanking(semanaId: number) {
  return requestApi<SemanaRankingEntry[]>(`/semana/${semanaId}/ranking`)
}
