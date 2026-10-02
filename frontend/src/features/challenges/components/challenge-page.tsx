'use client'

import { Download } from 'lucide-react'
import { useParams, useRouter } from 'next/navigation'
import Image from 'next/image'
import { useEffect, useState } from 'react'

import { useAuth } from '@/features/auth/auth-provider'
import {
  getChallenge,
  joinChallenge,
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
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string>()
  const [result, setResult] = useState<{ score: number }>()

  useEffect(() => {
    if (!authLoading && !user) router.replace('/semana/login')
  }, [authLoading, router, user])

  useEffect(() => {
    if (!user || !params.id) return
    getChallenge(params.id)
      .then((data) => {
        setChallenge(data)
        setInputAnswer('')
      })
      .catch((err: Error) => {
        if (err.message.includes('challenge has ended')) {
          router.replace('/semana/inicio')
          return
        }
        setError(err.message)
      })
  }, [params.id, router, user])

  async function join() {
    setBusy(true)
    setError(undefined)
    try {
      await joinChallenge(params.id)
      setChallenge(await getChallenge(params.id))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Não foi possível aceitar o desafio.')
    } finally {
      setBusy(false)
    }
  }

  async function submit() {
    setBusy(true)
    setError(undefined)
    try {
      setResult(await submitInput(params.id, inputAnswer))
      setChallenge((current) =>
        current ? { ...current, submitted_at: new Date().toISOString() } : current,
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

  return (
    <main className="mx-auto min-h-[calc(100svh-65px)] max-w-3xl px-6 py-16">
      <div className="space-y-4">
        <p className="font-[family-name:var(--font-semana-display)] text-sm uppercase text-primary">
          {challenge.scoring_type === 'quiz' ? 'Quiz' : 'Resposta livre'}
        </p>
        <h1 className="font-[family-name:var(--font-semana-display)] text-4xl font-bold uppercase">
          {challenge.title}
        </h1>
        {challenge.description && (
          <p className="text-lg text-white/80">{challenge.description}</p>
        )}
        <p className="text-xl text-white/80">{challenge.prompt}</p>
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
      ) : challenge.submitted_at || result ? (
        <section className="mt-10 border-[6px] border-white bg-card p-6 text-card-foreground">
          <h2 className="font-[family-name:var(--font-semana-display)] text-2xl uppercase">
            Respostas enviadas
          </h2>
          {result && <p className="mt-4 text-xl">Pontuação: {result.score}</p>}
        </section>
      ) : (
        <section className="mt-10 space-y-6 border-[6px] border-white bg-card p-6 text-card-foreground">
          {challenge.scoring_type !== 'input' ? (
            <p className="text-muted-foreground">
              Este formato de desafio ainda não está disponível.
            </p>
          ) : (
            <label className="block space-y-2">
              <span className="font-semibold">Sua resposta</span>
              <SemanaInput
                onChange={(event) => setInputAnswer(event.target.value)}
                value={inputAnswer}
              />
            </label>
          )}
          <SemanaButton
            disabled={busy || challenge.scoring_type !== 'input'}
            onClick={submit}
            type="button"
          >
            {busy ? 'Enviando…' : 'Enviar resposta'}
          </SemanaButton>
        </section>
      )}
    </main>
  )
}
