import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn } from '@/lib/utils'

import { semanaBody, semanaDisplay } from '../fonts'
import type { Sponsor, SponsorTalk } from '../sponsors'
import { SemanaButton } from './semana-button'
import { SponsorLogo } from './sponsor-logo'

// Brazil has no daylight saving time, so event times are always UTC-3.
const BRASILIA_OFFSET = '-03:00'

const dayFormatter = new Intl.DateTimeFormat('pt-BR', {
  weekday: 'long',
  day: 'numeric',
  month: 'long',
  timeZone: 'America/Sao_Paulo',
})

const smallButtonClassName =
  'border-4 px-4 py-2 text-sm shadow-[0_4px_0_hsl(var(--semana-contrast))] active:shadow-[0_2px_0_hsl(var(--semana-contrast))]'

function talkSchedule(talk: SponsorTalk) {
  const [start, end] = talk.horario.split('-').map((time) => time.trim())
  const startsAt = new Date(`${talk.data}T${start}:00${BRASILIA_OFFSET}`)
  const endsAt = new Date(`${talk.data}T${end}:00${BRASILIA_OFFSET}`)
  const toCalendarDate = (date: Date) => date.toISOString().replace(/[-:]|\.\d{3}/g, '')

  const calendarUrl = new URL('https://calendar.google.com/calendar/render')
  calendarUrl.searchParams.set('action', 'TEMPLATE')
  calendarUrl.searchParams.set('text', talk.titulo)
  calendarUrl.searchParams.set('details', talk.descricao)
  calendarUrl.searchParams.set(
    'dates',
    `${toCalendarDate(startsAt)}/${toCalendarDate(endsAt)}`,
  )

  return {
    label: `${dayFormatter.format(startsAt)}, ${start.replace(':', 'h')} às ${end.replace(':', 'h')}`,
    calendarUrl: calendarUrl.toString(),
  }
}

function ExternalLink({ href, children }: { href: string; children: string }) {
  return (
    <SemanaButton asChild className={smallButtonClassName}>
      <a href={href} rel="noopener noreferrer" target="_blank">
        {children}
        <span className="sr-only"> (abre em nova aba)</span>
      </a>
    </SemanaButton>
  )
}

export function SponsorDialog({ sponsor }: { sponsor: Sponsor }) {
  const talk = sponsor.palestra
  const schedule = talk && talkSchedule(talk)

  return (
    <Dialog>
      <DialogTrigger className="whitespace-nowrap px-3 py-1 font-[family-name:var(--font-semana-display)] text-sm sm:text-base font-bold uppercase text-white underline-offset-4 hover:underline focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring">
        Saber mais +<span className="sr-only"> sobre {sponsor.nome}</span>
      </DialogTrigger>
      <DialogContent
        className={cn(
          'semana-theme max-h-[90svh] w-[calc(100%-2rem)] max-w-md gap-0 overflow-y-auto rounded-none border-[6px] border-white bg-[hsl(var(--semana-sponsor))] p-0 font-[family-name:var(--font-semana-body)] text-white sm:rounded-none [&>button]:text-white [&>button]:opacity-100',
          semanaBody.variable,
          semanaDisplay.variable,
        )}
      >
        <div className="flex flex-col gap-4 p-6 pr-12">
          <SponsorLogo className="h-24" sponsor={sponsor} />
          <DialogTitle className="font-[family-name:var(--font-semana-display)] text-2xl font-bold uppercase">
            {sponsor.nome}
          </DialogTitle>
          <DialogDescription
            className={cn('text-base text-white/90', !sponsor.descricao && 'sr-only')}
          >
            {sponsor.descricao ?? `Patrocinador da Semana da Computação.`}
          </DialogDescription>
          {sponsor.site && <ExternalLink href={sponsor.site}>Site</ExternalLink>}
        </div>

        {talk && schedule && (
          <Tabs defaultValue="palestra">
            <TabsList className="grid h-auto w-full grid-cols-2 rounded-none border-y-[6px] border-white bg-transparent p-0">
              {['palestra', 'palestrante'].map((value) => (
                <TabsTrigger
                  className="rounded-none py-3 font-[family-name:var(--font-semana-display)] text-sm font-bold uppercase text-white/80 data-[state=active]:bg-[hsl(var(--semana-sponsor-soft))] data-[state=active]:text-white data-[state=active]:shadow-none"
                  key={value}
                  value={value}
                >
                  {value}
                </TabsTrigger>
              ))}
            </TabsList>
            <TabsContent className="mt-0 space-y-3 p-6" value="palestra">
              <h3 className="text-xl font-bold">{talk.titulo}</h3>
              <p className="font-bold text-primary first-letter:uppercase">
                {schedule.label}
              </p>
              <p className="text-white/90">{talk.descricao}</p>
              <ExternalLink href={schedule.calendarUrl}>Salvar na agenda</ExternalLink>
            </TabsContent>
            <TabsContent className="mt-0 space-y-3 p-6" value="palestrante">
              <h3 className="text-xl font-bold text-primary">{talk.palestrante}</h3>
              <p className="text-white/90">{talk.sobre}</p>
            </TabsContent>
          </Tabs>
        )}
      </DialogContent>
    </Dialog>
  )
}
