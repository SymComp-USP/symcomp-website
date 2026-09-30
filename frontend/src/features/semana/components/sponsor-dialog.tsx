import { ChevronLeft, ChevronRight, Link as LinkIcon, X } from 'lucide-react'
import Image from 'next/image'
import { BsInstagram, BsLinkedin, BsYoutube } from 'react-icons/bs'

import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from '@/components/ui/dialog'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { cn } from '@/lib/utils'

import { semanaBody, semanaDisplay } from '../fonts'
import type { Sponsor, SponsorTalk } from '../sponsors'
import { SponsorLogo } from './sponsor-logo'

// Brazil has no daylight saving time, so event times are always UTC-3.
const BRASILIA_OFFSET = '-03:00'

const navButtonClassName =
  'flex size-10 shrink-0 items-center justify-center text-[hsl(var(--semana-sponsor-soft))] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-30'

const socialIcons = {
  linkedin: { icon: BsLinkedin, label: 'LinkedIn' },
  youtube: { icon: BsYoutube, label: 'YouTube' },
  instagram: { icon: BsInstagram, label: 'Instagram' },
}

function talkSchedule(talk: SponsorTalk) {
  const [start, end] = talk.horario.split('-').map((time) => time.trim())
  const toDate = (time: string) => new Date(`${talk.data}T${time}:00${BRASILIA_OFFSET}`)
  const toCalendarDate = (date: Date) => date.toISOString().replace(/[-:]|\.\d{3}/g, '')

  const calendarUrl = new URL('https://calendar.google.com/calendar/render')
  calendarUrl.searchParams.set('action', 'TEMPLATE')
  calendarUrl.searchParams.set('text', talk.titulo)
  calendarUrl.searchParams.set('details', talk.descricao)
  calendarUrl.searchParams.set(
    'dates',
    `${toCalendarDate(toDate(start))}/${toCalendarDate(toDate(end))}`,
  )

  const [, month, day] = talk.data.split('-')
  return {
    label: `${day}/${month} às ${start.replace(':', 'h')}`,
    calendarUrl: calendarUrl.toString(),
  }
}

function initials(name: string) {
  return name
    .split(/\s+/)
    .slice(0, 2)
    .map((word) => word[0])
    .join('')
    .toUpperCase()
}

function SponsorDetails({ sponsor }: { sponsor: Sponsor }) {
  const talk = sponsor.palestra
  const schedule = talk && talkSchedule(talk)

  return (
    <>
      <div className="flex items-center gap-4 p-5 pr-12">
        <SponsorLogo className="size-24" sponsor={sponsor} />
        <div className="min-w-0 space-y-2">
          <DialogTitle className="text-xl font-bold uppercase leading-tight">
            {sponsor.nome}
          </DialogTitle>
          <DialogDescription
            className={cn('text-sm text-white/90', !sponsor.descricao && 'sr-only')}
          >
            {sponsor.descricao ?? 'Patrocinador da Semana da Computação.'}
          </DialogDescription>
          {sponsor.site && (
            <a
              className="inline-flex items-center gap-2 bg-[hsl(var(--semana-sponsor-soft))] px-3 py-1 text-sm font-bold uppercase text-white hover:underline focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring"
              href={sponsor.site}
              rel="noopener noreferrer"
              target="_blank"
            >
              Site
              <LinkIcon aria-hidden="true" className="size-4" />
              <span className="sr-only"> (abre em nova aba)</span>
            </a>
          )}
        </div>
      </div>

      {talk && schedule && (
        <Tabs defaultValue="palestra">
          <TabsList className="grid h-auto w-full grid-cols-2 gap-1 rounded-none bg-transparent p-0 px-1">
            {['palestra', 'palestrante'].map((value) => (
              <TabsTrigger
                className="rounded-none border-2 border-white py-2 text-sm font-bold uppercase text-white data-[state=active]:bg-[hsl(var(--semana-sponsor-soft))] data-[state=active]:text-white data-[state=active]:shadow-none"
                key={value}
                value={value}
              >
                {value}
              </TabsTrigger>
            ))}
          </TabsList>

          <TabsContent
            className="mt-1 space-y-3 border-t-2 border-white p-5"
            value="palestra"
          >
            <h3 className="text-lg font-bold uppercase leading-tight">{talk.titulo}</h3>
            <p className="font-bold uppercase text-primary">{schedule.label}</p>
            <p className="text-white/90">{talk.descricao}</p>
            <div className="flex justify-center pt-3">
              <a
                className="semana-pixel-notch block bg-[hsl(var(--semana-sponsor-soft))] p-1 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring"
                href={schedule.calendarUrl}
                rel="noopener noreferrer"
                target="_blank"
              >
                <span className="semana-pixel-notch block bg-[hsl(var(--semana-contrast))] px-6 py-2 text-sm font-bold uppercase text-white">
                  Salvar na agenda
                  <span className="sr-only"> (abre em nova aba)</span>
                </span>
              </a>
            </div>
          </TabsContent>

          <TabsContent
            className="mt-1 space-y-4 border-t-2 border-white p-5"
            value="palestrante"
          >
            <div className="flex items-center gap-4">
              {talk.palestranteFoto ? (
                <Image
                  alt=""
                  className="size-16 shrink-0 rounded-full border-4 border-white object-cover"
                  height={64}
                  src={talk.palestranteFoto}
                  width={64}
                />
              ) : (
                <span
                  aria-hidden="true"
                  className="flex size-16 shrink-0 items-center justify-center rounded-full border-4 border-white bg-[hsl(var(--semana-sponsor-soft))] text-lg font-bold"
                >
                  {initials(talk.palestrante)}
                </span>
              )}
              <h3 className="text-lg font-bold uppercase leading-tight">
                {talk.palestrante}
              </h3>
            </div>
            <p className="text-white/90">{talk.sobre}</p>
            {talk.redes && (
              <ul className="flex justify-center gap-3">
                {Object.entries(socialIcons).map(([key, { icon: Icon, label }]) => {
                  const href = talk.redes?.[key as keyof typeof socialIcons]
                  if (!href) return null
                  return (
                    <li key={key}>
                      <a
                        aria-label={`${label} de ${talk.palestrante}`}
                        className="flex size-11 items-center justify-center rounded-full bg-[hsl(var(--semana-sponsor-soft))] text-white focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring"
                        href={href}
                        rel="noopener noreferrer"
                        target="_blank"
                      >
                        <Icon aria-hidden="true" size={20} />
                      </a>
                    </li>
                  )
                })}
              </ul>
            )}
          </TabsContent>
        </Tabs>
      )}
    </>
  )
}

export function SponsorDialog({
  sponsors,
  index,
  onIndexChange,
}: {
  sponsors: Sponsor[]
  index: number | null
  onIndexChange: (index: number | null) => void
}) {
  const sponsor = index === null ? undefined : sponsors[index]

  return (
    <Dialog
      onOpenChange={(open) => {
        if (!open) onIndexChange(null)
      }}
      open={sponsor !== undefined}
    >
      <DialogContent
        className={cn(
          'semana-theme flex w-[calc(100%-1rem)] max-w-xl flex-col items-center gap-4 border-0 bg-transparent p-0 font-[family-name:var(--font-semana-body)] text-white shadow-none sm:rounded-none [&>button:last-child]:hidden',
          semanaBody.variable,
          semanaDisplay.variable,
        )}
      >
        {sponsor && index !== null && (
          <>
            <div className="flex w-full items-center gap-1">
              <button
                aria-label="Patrocinador anterior"
                className={navButtonClassName}
                disabled={index === 0}
                onClick={() => onIndexChange(index - 1)}
                type="button"
              >
                <ChevronLeft aria-hidden="true" className="size-9" strokeWidth={4} />
              </button>

              <div className="semana-pixel-notch min-w-0 flex-1 bg-white p-1">
                <div className="semana-pixel-notch relative max-h-[80svh] overflow-y-auto bg-[hsl(var(--semana-contrast))]">
                  <DialogClose className="absolute right-3 top-3 z-10 flex size-8 items-center justify-center text-white focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring">
                    <X aria-hidden="true" />
                    <span className="sr-only">Fechar</span>
                  </DialogClose>
                  <SponsorDetails key={index} sponsor={sponsor} />
                </div>
              </div>

              <button
                aria-label="Próximo patrocinador"
                className={navButtonClassName}
                disabled={index === sponsors.length - 1}
                onClick={() => onIndexChange(index + 1)}
                type="button"
              >
                <ChevronRight aria-hidden="true" className="size-9" strokeWidth={4} />
              </button>
            </div>

            {sponsors.length > 1 && (
              <div className="flex gap-2">
                {sponsors.map((item, dotIndex) => (
                  <button
                    aria-current={dotIndex === index ? 'true' : undefined}
                    aria-label={`Ir para o patrocinador ${dotIndex + 1} de ${sponsors.length}`}
                    className={cn(
                      'size-3 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring',
                      dotIndex === index
                        ? 'bg-[hsl(var(--semana-sponsor-soft))]'
                        : 'bg-white',
                    )}
                    key={item.nome}
                    onClick={() => onIndexChange(dotIndex)}
                    type="button"
                  />
                ))}
              </div>
            )}
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
