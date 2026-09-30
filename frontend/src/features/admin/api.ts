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
  return requestApi<AdminSemana[]>('/admin/semana')
}

export function createAdminSemana(input: { nome: string; ano: number }) {
  return requestApi<AdminSemana>('/admin/semana', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function updateAdminSemana(
  id: number,
  input: Partial<Pick<AdminSemana, 'nome' | 'ano'>>,
) {
  return requestApi<AdminSemana>(`/admin/semana/${id}`, {
    method: 'PATCH',
    body: JSON.stringify(input),
  })
}

export function deleteAdminSemana(id: number) {
  return requestApi<void>(`/admin/semana/${id}`, { method: 'DELETE' })
}
