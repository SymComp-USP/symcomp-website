import { mockSchedule } from '../data/mock-schedule'
import { ActivityCard } from './activity-card'

const dayFormatter = new Intl.DateTimeFormat('pt-BR', {
  day: '2-digit',
  month: 'long',
  timeZone: 'America/Sao_Paulo',
})

const weekdayFormatter = new Intl.DateTimeFormat('pt-BR', {
  weekday: 'long',
  timeZone: 'America/Sao_Paulo',
})

export function SchedulePage() {
  const days = Map.groupBy(mockSchedule, (activity) => activity.startsAt.slice(0, 10))

  return (
    <main className="mx-auto min-h-[calc(100svh-65px)] max-w-4xl px-6 py-16">
      <div className="mb-12 max-w-2xl space-y-3">
        <p className="font-[family-name:var(--font-semana-display)] text-sm font-bold uppercase tracking-[0.2em] text-primary">
          Semana da Computação
        </p>
        <h1 className="font-[family-name:var(--font-semana-display)] text-4xl font-bold uppercase tracking-tight sm:text-5xl">
          Programação
        </h1>
        <p className="text-xl text-white/80">
          Uma prévia da programação. Horários e participantes ainda podem mudar.
        </p>
      </div>

      <div className="space-y-12">
        {[...days.entries()].map(([date, activities]) => {
          const day = new Date(`${date}T12:00:00-03:00`)
          return (
            <section key={date} aria-labelledby={`day-${date}`}>
              <div className="mb-5 border-b-[6px] border-[hsl(var(--semana-contrast))] pb-3">
                <h2
                  className="font-[family-name:var(--font-semana-display)] text-2xl font-bold capitalize"
                  id={`day-${date}`}
                >
                  {weekdayFormatter.format(day)}
                </h2>
                <p className="text-lg text-white/75">{dayFormatter.format(day)}</p>
              </div>
              <div className="space-y-4">
                {activities.map((activity) => (
                  <ActivityCard activity={activity} key={activity.uid} />
                ))}
              </div>
            </section>
          )
        })}
      </div>
    </main>
  )
}
