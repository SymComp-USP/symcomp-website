'use client'

import { useEffect, useState } from 'react'

import { PixelChevron } from '@/features/semana/components/pixel-chevron'
import { SEMANA_YEAR } from '@/features/semana/config'
import { cn } from '@/lib/utils'

import { listScheduleActivities, listScheduleWeeks, mapActivity } from '../api'
import type { Activity } from '../types'
import { ActivityCard } from './activity-card'
import { ActivityDialog } from './activity-dialog'

const EVENT_DAYS = [
  { date: '2026-10-05', label: 'Segunda' },
  { date: '2026-10-06', label: 'Terça' },
  { date: '2026-10-07', label: 'Quarta' },
  { date: '2026-10-08', label: 'Quinta' },
  { date: '2026-10-09', label: 'Sexta' },
]

// en-CA formats as YYYY-MM-DD, matching EVENT_DAYS keys.
const dateKeyFormatter = new Intl.DateTimeFormat('en-CA', {
  day: '2-digit',
  month: '2-digit',
  timeZone: 'America/Sao_Paulo',
  year: 'numeric',
})

function dateKey(date: Date | string) {
  return dateKeyFormatter.format(new Date(date))
}

function shortDate(date: string) {
  const [, month, day] = date.split('-')
  return `${day}/${month}`
}

export function SchedulePage() {
  const [activities, setActivities] = useState<Activity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [dayIndex, setDayIndex] = useState(0)
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  useEffect(() => {
    const today = EVENT_DAYS.findIndex((day) => day.date === dateKey(new Date()))
    if (today !== -1) setDayIndex(today)

    listScheduleWeeks()
      .then((weeks) => {
        const week = weeks.find((item) => item.ano === SEMANA_YEAR)
        if (!week) throw new Error('Semana da Computação 2026 não encontrada.')
        return listScheduleActivities(week.id)
      })
      .then((items) => setActivities(items.map(mapActivity)))
      .catch((reason: Error) => setError(reason.message))
      .finally(() => setLoading(false))
  }, [])

  const day = EVENT_DAYS[dayIndex]
  const dayActivities = activities.filter(
    (activity) => dateKey(activity.startsAt) === day.date,
  )

  return (
    <main className="min-h-full overflow-x-clip bg-[hsl(var(--semana-schedule))] text-white">
      <div className="mx-auto max-w-2xl px-7 py-12 sm:px-10 sm:py-16">
        <div className="space-y-2 text-center">
          <h1 className="font-[family-name:var(--font-semana-display)] text-4xl font-bold uppercase [text-shadow:0_3px_0_hsl(var(--semana-schedule-ink))] sm:text-6xl">
            Cronograma
          </h1>
          <p className="text-lg text-[hsl(var(--semana-schedule-ink))] sm:text-xl">
            Veja todas as palestras do evento!
          </p>
        </div>

        <nav aria-label="Dias do evento" className="mt-8 flex flex-col items-center">
          <div className="flex gap-2">
            {EVENT_DAYS.map((item, index) => (
              <button
                aria-current={index === dayIndex ? 'date' : undefined}
                aria-label={`${item.label}, ${shortDate(item.date)}`}
                className={cn(
                  'size-2.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring',
                  index === dayIndex
                    ? 'bg-white'
                    : 'bg-[hsl(var(--semana-schedule-ink))] hover:opacity-80',
                )}
                key={item.date}
                onClick={() => setDayIndex(index)}
                type="button"
              />
            ))}
          </div>

          <div className="mt-4 flex w-full items-center justify-between gap-2">
            <button
              aria-label="Dia anterior"
              className="p-2 text-[hsl(var(--semana-schedule-ink))] transition-opacity focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring disabled:cursor-default"
              disabled={dayIndex === 0}
              onClick={() => setDayIndex(dayIndex - 1)}
              type="button"
            >
              <PixelChevron className="h-8 w-auto" direction="left" />
            </button>
            <div className="flex flex-col items-center">
              <p
                aria-live="polite"
                className="semana-notch min-w-48 bg-[hsl(var(--semana-schedule-ink))] px-7 py-4 text-center font-[family-name:var(--font-semana-display)] text-3xl font-normal uppercase leading-none tracking-tight [--notch:10px] sm:min-w-60 sm:text-4xl"
              >
                {day.label}
              </p>
              <p className="mt-1 font-[family-name:var(--font-semana-display)] text-xl font-bold tracking-tighter text-[hsl(var(--semana-schedule-ink))]">
                {shortDate(day.date)}
              </p>
            </div>
            <button
              aria-label="Próximo dia"
              className="p-2 text-[hsl(var(--semana-schedule-ink))] transition-opacity focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring disabled:cursor-default"
              disabled={dayIndex === EVENT_DAYS.length - 1}
              onClick={() => setDayIndex(dayIndex + 1)}
              type="button"
            >
              <PixelChevron className="h-8 w-auto" />
            </button>
          </div>
        </nav>

        <section aria-label={`Atividades de ${day.label}`} className="mt-8">
          {loading && <p className="text-center text-lg">Carregando programação…</p>}
          {error && (
            <p className="text-center text-lg" role="alert">
              {error}
            </p>
          )}
          {!loading && !error && !dayActivities.length && (
            <p className="text-center text-lg">Programação em breve.</p>
          )}
          <ol>
            {dayActivities.map((activity, index) => (
              <li key={activity.uid}>
                {index > 0 && (
                  <div
                    aria-hidden="true"
                    className="mx-auto h-8 w-2 bg-[hsl(var(--semana-schedule-ink))]"
                  />
                )}
                <ActivityCard activity={activity} onOpen={() => setOpenIndex(index)} />
              </li>
            ))}
          </ol>
          <ActivityDialog
            activities={dayActivities}
            index={openIndex}
            onIndexChange={setOpenIndex}
          />
        </section>
      </div>
    </main>
  )
}
