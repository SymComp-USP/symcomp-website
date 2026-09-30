import { requestApi } from '@/features/auth/api'

export type Challenge = {
  id: string
  title: string
  prompt: string
  scoring_type: 'input' | 'quiz' | 'manual'
  finishes_at: string
  resource_urls: string[]
  image_url: string | null
}

export type ChallengeDetails = Challenge & {
  questions: unknown[]
  is_participant: boolean
  submitted_at: string | null
}

export function getChallenge(id: string) {
  return requestApi<ChallengeDetails>(`/challenge/${id}`)
}

export function joinChallenge(id: string) {
  return requestApi(`/challenge/${id}/join`, { method: 'POST' })
}

export function submitInput(id: string, answer: string) {
  return requestApi<{ submitted_at: string; score: number }>(`/challenge/${id}/input`, {
    method: 'POST',
    body: JSON.stringify({ answer }),
  })
}

export function mediaUrl(path: string) {
  if (path.startsWith('http')) return path
  return `${process.env.NEXT_PUBLIC_API_URL ?? ''}${path}`
}
