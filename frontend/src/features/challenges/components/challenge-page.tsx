'use client'

import { Download } from 'lucide-react'
import { useParams, useRouter } from 'next/navigation'
import Image from 'next/image'
import { useEffect, useState } from 'react'

import { useAuth } from '@/features/auth/auth-provider'
import {
  getChallenge,
  joinChallenge,
  saveChallengeAnswers,
  submitChallenge,
  submitInput,
  type ChallengeDetails,
  mediaUrl,
} from '../api'
import { SemanaButton } from '@/features/semana/components/semana-button'
import { SemanaInput } from '@/features/semana/components/semana-input'

export function ChallengePage() {
  const params = useParams<{ id: string }>()
  const router = useRouter()
  const { user, loading: authLoading } = useAuth()
  const [challenge, setChallenge] = useState<ChallengeDetails>()
  const [inputAnswer, setInputAnswer] = useState('')
  const [answers, setAnswers] = useState<Record<string, string>>({})
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string>()
  const [result, setResult] = useState<{
    submitted_at: string | null
    score: number
  }>()

  useEffect(() => {
    if (!authLoading && !user) router.replace('/semana/login')
  }, [authLoading, router, user])

  useEffect(() => {
    if (!user || !params.id) return
    getChallenge(params.id)
      .then((data) => {
        setChallenge(data)
        setInputAnswer('')
        setAnswers(
          Object.fromEntries(
            data.questions.map((question) => [
              question.id,
              question.current_answer ?? '',
            ]),
          ),
        )
      })
      .catch((err: Error) => {
        if (err.message.includes('challenge has ended')) {
          router.replace('/semana')
          return
        }
        setError(err.message)
      })
  }, [params.id, router, user])

  async function join() {
    setBusy(true)
    setError(undefined)
    try {
      const participant = await joinChallenge(params.id)
      setChallenge((current) =>
        current
          ? {
              ...current,
              is_participant: true,
              submitted_at: participant.submitted_at,
              score: participant.score,
            }
          : current,
      )
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível aceitar o desafio.')
    } finally {
      setBusy(false)
    }
  }

  async function submit() {
    if (!challenge) return
    setBusy(true)
    setError(undefined)
    setResult(undefined)
    try {
      let submission
      if (challenge.scoring_type === 'input') {
        submission = await submitInput(params.id, inputAnswer)
      } else if (challenge.scoring_type === 'quiz') {
        await saveChallengeAnswers(
          params.id,
          challenge.questions.map((question) => ({
            question_id: question.id,
            answer: answers[question.id] ?? '',
          })),
        )
        submission = await submitChallenge(params.id)
      } else {
        throw new Error('Este formato de desafio não está disponível.')
      }
      setResult(submission)
      setChallenge((current) =>
        current
          ? {
              ...current,
              submitted_at: submission.submitted_at,
              score: submission.score,
            }
          : current,
      )
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Não foi possível enviar suas respostas.',
      )
    } finally {
      setBusy(false)
    }
  }

  async function downloadImage() {
    if (!challenge?.image_url) return
    const response = await fetch(mediaUrl(challenge.image_url))
    const blob = await response.blob()
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = `${challenge.title.toLowerCase().replace(/[^a-z0-9]+/g, '-')}.jpg`
    link.click()
    URL.revokeObjectURL(link.href)
  }

  if (authLoading || !user || (!challenge && !error)) {
    return <main className="mx-auto max-w-4xl px-6 py-16">Carregando desafio…</main>
  }

  if (error && !challenge) {
    return <main className="mx-auto max-w-4xl px-6 py-16 text-destructive">{error}</main>
  }

  if (!challenge) return null

  const hasQuizAttempt =
    challenge.scoring_type === 'quiz' &&
    challenge.questions.some((question) => question.current_answer !== null)
  const showRetryFeedback =
    (result !== undefined && result.submitted_at === null) ||
    (challenge.scoring_type === 'quiz' && !challenge.submitted_at && hasQuizAttempt)

  return (
    <main className="mx-auto min-h-[calc(100svh-65px)] max-w-3xl px-6 py-16">
      <div className="space-y-4">
        <p className="font-[family-name:var(--font-semana-display)] text-sm uppercase text-primary">
          {challenge.scoring_type === 'quiz' ? 'Quiz' : 'Resposta livre'}
        </p>
        <h1 className="font-[family-name:var(--font-semana-display)] text-4xl font-bold uppercase">
          {challenge.title}
        </h1>
        {challenge.description && <p className="text-lg">{challenge.description}</p>}
        <p className="text-xl">{challenge.prompt}</p>
        {challenge.image_url && (
          <div className="space-y-3">
            <Image
              alt="Imagem do desafio"
              className="max-h-96 w-full object-contain"
              height={600}
              src={mediaUrl(challenge.image_url)}
              unoptimized
              width={900}
            />
            <button
              className="inline-flex items-center gap-2 text-sm font-semibold text-primary underline-offset-4 hover:underline"
              onClick={downloadImage}
              type="button"
            >
              <Download size={16} /> Baixar imagem
            </button>
          </div>
        )}
      </div>

      {error && <p className="mt-6 text-destructive">{error}</p>}

      {!challenge.is_participant ? (
        <section className="mt-10 space-y-5 border-[6px] border-white bg-card p-6 text-card-foreground">
          <p>Aceite este desafio para responder e pontuar.</p>
          <SemanaButton disabled={busy} onClick={join}>
            {busy ? 'Entrando…' : 'Aceitar desafio'}
          </SemanaButton>
        </section>
      ) : challenge.submitted_at || result?.submitted_at ? (
        <section className="mt-10 border-[6px] border-white bg-card p-6 text-card-foreground">
          <h2 className="font-[family-name:var(--font-semana-display)] text-2xl uppercase">
            {challenge.scoring_type === 'input'
              ? 'Resposta correta'
              : challenge.scoring_type === 'quiz'
                ? 'Quiz concluído'
                : 'Respostas enviadas'}
          </h2>
          <p className="mt-4 text-xl">
            Pontuação: {result?.score ?? challenge.score ?? 0}
          </p>
        </section>
      ) : (
        <section className="mt-10 space-y-6 border-[6px] border-white bg-card p-6 text-card-foreground">
          {showRetryFeedback && (
            <div className="text-destructive" role="status">
              <p>
                {challenge.scoring_type === 'quiz'
                  ? 'Ainda há respostas incorretas. Tente novamente.'
                  : 'Resposta incorreta. Tente novamente.'}
              </p>
              {challenge.scoring_type === 'quiz' && (
                <p className="mt-1">
                  Pontuação parcial: {result?.score ?? challenge.score ?? 0}
                </p>
              )}
            </div>
          )}
          {challenge.scoring_type === 'manual' ? (
            <p className="text-lg font-semibold">
              Complete o desafio e reporte à equipe para ganhar os seus pontos!
            </p>
          ) : challenge.scoring_type === 'input' ? (
            <label className="block space-y-2">
              <span className="font-semibold">Sua resposta</span>
              <SemanaInput
                onChange={(event) => {
                  setInputAnswer(event.target.value)
                  setResult(undefined)
                }}
                value={inputAnswer}
              />
            </label>
          ) : challenge.scoring_type === 'quiz' ? (
            <div className="space-y-5">
              {challenge.questions.map((question, index) => (
                <label className="block space-y-2" key={question.id}>
                  <span className="font-semibold">
                    {index + 1}. {question.prompt}
                  </span>
                  <SemanaInput
                    onChange={(event) => {
                      setAnswers((current) => ({
                        ...current,
                        [question.id]: event.target.value,
                      }))
                      setResult(undefined)
                    }}
                    value={answers[question.id] ?? ''}
                  />
                </label>
              ))}
            </div>
          ) : null}
          {challenge.scoring_type !== 'manual' && (
            <SemanaButton disabled={busy} onClick={submit} type="button">
              {busy ? 'Enviando…' : 'Enviar resposta'}
            </SemanaButton>
          )}
        </section>
      )}
    </main>
  )
}
