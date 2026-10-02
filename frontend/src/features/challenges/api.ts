import { requestApi } from '@/features/auth/api'

export type Challenge = {
  id: string
  title: string
  description: string
  prompt: string
  scoring_type: 'input' | 'quiz' | 'manual'
  finishes_at: string
  resource_urls: string[]
  image_url: string | null
}

export type ChallengeQuestion = {
  id: string
  prompt: string
  current_answer: string | null
}

export type ChallengeSubmission = {
  submitted_at: string | null
  score: number
}

type ChallengePage = {
  items: Challenge[]
  total: number
  limit: number
  offset: number
}

export type ChallengeDetails = Challenge & {
  questions: ChallengeQuestion[]
  is_participant: boolean
  submitted_at: string | null
  score: number | null
}

export function getChallenge(id: string) {
  return requestApi<ChallengeDetails>(`/challenge/${id}`, { cache: 'no-store' })
}

export function joinChallenge(id: string) {
  return requestApi<{ submitted_at: string | null; score: number }>(
    `/challenge/${id}/join`,
    { method: 'POST' },
  )
}

export function listChallenges(limit = 20, offset = 0) {
  return requestApi<ChallengePage>(`/challenge?limit=${limit}&offset=${offset}`, {
    cache: 'no-store',
  })
}

export function saveChallengeAnswers(
  id: string,
  answers: { question_id: string; answer: string }[],
) {
  return requestApi<void>(`/challenge/${id}/answer/all`, {
    method: 'POST',
    body: JSON.stringify(answers),
  })
}

export function submitChallenge(id: string) {
  return requestApi<ChallengeSubmission>(`/challenge/${id}/submit`, {
    method: 'POST',
  })
}

export function submitInput(id: string, answer: string) {
  return requestApi<ChallengeSubmission>(`/challenge/${id}/input`, {
    method: 'POST',
    body: JSON.stringify({ answer }),
  })
}

export function mediaUrl(path: string) {
  if (path.startsWith('http')) return path
  return `${process.env.NEXT_PUBLIC_API_URL ?? ''}${path}`
}
