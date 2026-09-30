import { requestApi } from '@/features/auth/api'

export type AdminUser = {
  id: string
  name: string
  email: string
  is_admin: boolean
  is_verified: boolean
  created_at: string
}

export type AdminChallenge = {
  id: string
  title: string
  prompt: string
  scoring_type: 'input' | 'quiz' | 'manual'
  finishes_at: string
  semana_id: number | null
  points_value: number
}

export type AdminSemana = {
  id: number
  nome: string
  ano: number
  challenge_count: number
  participant_count: number
}

export type AdminAtividade = {
  id: string
  semana_id: number
  tipo: 'palestra' | 'workshop' | 'encerramento' | 'conversa' | 'coffee_break'
  titulo: string
  status: 'provisoria' | 'confirmada'
  comeca_as: string
  termina_as: string
  codigo: string
  pontos: number
  horas: number
}

export type AdminPresenca = {
  id: string
  atividade_id: string
  user_id: string | null
  nome: string
  email: string
  horas: number
}

type Page<T> = { items: T[]; total: number; limit: number; offset: number }

export function listAdminUsers() {
  return requestApi<Page<AdminUser>>('/admin/users?limit=100')
}

export function createAdminUser(input: {
  name: string
  email: string
  password: string
  is_admin: boolean
  is_verified: boolean
}) {
  return requestApi<AdminUser>('/admin/users', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function updateAdminUser(id: string, input: Partial<AdminUser>) {
  return requestApi<AdminUser>(`/admin/users/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(input),
  })
}

export function deleteAdminUser(id: string) {
  return requestApi<void>(`/admin/users/${id}`, { method: 'DELETE' })
}

export function listAdminChallenges() {
  return requestApi<Page<AdminChallenge>>('/admin/challenge?limit=100')
}

export function createAdminChallenge(input: {
  title: string
  prompt: string
  scoring_type: AdminChallenge['scoring_type']
  finishes_at: string
  points_value: number
  input_answer: string
  semana_id?: number
}) {
  return requestApi<AdminChallenge>('/admin/challenge', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function uploadAdminChallengeImage(id: string, file: File) {
  const formData = new FormData()
  formData.append('file', file)
  return requestApi<AdminChallenge>(`/admin/challenge/${id}/image`, {
    method: 'PUT',
    body: formData,
  })
}

export function deleteAdminChallenge(id: string) {
  return requestApi<void>(`/admin/challenge/${id}`, { method: 'DELETE' })
}

export function listAdminSemanas() {
  return requestApi<AdminSemana[]>('/admin/semanas')
}

export function createAdminSemana(input: { nome: string; ano: number }) {
  return requestApi<AdminSemana>('/admin/semanas', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function updateAdminSemana(
  id: number,
  input: Partial<Pick<AdminSemana, 'nome' | 'ano'>>,
) {
  return requestApi<AdminSemana>(`/admin/semanas/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(input),
  })
}

export function deleteAdminSemana(id: number) {
  return requestApi<void>(`/admin/semanas/${id}`, { method: 'DELETE' })
}

export function listAdminAtividades(semanaId: number) {
  return requestApi<AdminAtividade[]>(`/admin/semanas/${semanaId}/atividades`)
}

export function createAdminAtividade(
  semanaId: number,
  input: Omit<AdminAtividade, 'id' | 'semana_id' | 'codigo'>,
) {
  return requestApi<AdminAtividade>(`/admin/semanas/${semanaId}/atividades`, {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function deleteAdminAtividade(semanaId: number, id: string) {
  return requestApi<void>(`/admin/semanas/${semanaId}/atividades/${id}`, {
    method: 'DELETE',
  })
}

export function regenerateAdminAtividadeCode(semanaId: number, id: string) {
  return requestApi<AdminAtividade>(
    `/admin/semanas/${semanaId}/atividades/${id}/regenerar-codigo`,
    { method: 'POST' },
  )
}

export function listAdminPresencas(semanaId: number, atividadeId: string) {
  return requestApi<AdminPresenca[]>(
    `/admin/semanas/${semanaId}/atividades/${atividadeId}/presencas`,
  )
}

export function createAdminPresenca(
  semanaId: number,
  atividadeId: string,
  input: { nome?: string; email: string },
) {
  return requestApi<AdminPresenca>(
    `/admin/semanas/${semanaId}/atividades/${atividadeId}/presencas`,
    { method: 'POST', body: JSON.stringify(input) },
  )
}

export function deleteAdminPresenca(
  semanaId: number,
  atividadeId: string,
  presencaId: string,
) {
  return requestApi<void>(
    `/admin/semanas/${semanaId}/atividades/${atividadeId}/presencas/${presencaId}`,
    { method: 'DELETE' },
  )
}
