import { MapPin, X, Youtube } from 'lucide-react'
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
import { semanaBody, semanaDisplay } from '@/features/semana/fonts'
import { PixelChevron } from '@/features/semana/components/pixel-chevron'
import { sponsors } from '@/features/semana/sponsors'
import { cn } from '@/lib/utils'

import { googleCalendarUrl } from '../calendar'
import { formatTimeRange } from '../time'
import { type Activity, activityTypeLabels, type Speaker } from '../types'

const navButtonClassName =
  'hidden size-10 shrink-0 items-center sm:flex justify-center text-[hsl(var(--secondary))] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-30'

const socialIcons = {
  linkedin: { icon: BsLinkedin, label: 'LinkedIn' },
  youtube: { icon: BsYoutube, label: 'YouTube' },
  instagram: { icon: BsInstagram, label: 'Instagram' },
}

function initials(name: string) {
  return name
    .split(/\s+/)
    .slice(0, 2)
    .map((word) => word[0])
    .join('')
    .toUpperCase()
}

function SpeakerSocials({ speaker }: { speaker: Speaker }) {
  const links = Object.entries(socialIcons).filter(
    ([key]) => speaker[key as keyof typeof socialIcons],
  )
  if (!links.length) return null

  return (
    <ul className="flex justify-center gap-3">
      {links.map(([key, { icon: Icon, label }]) => (
        <li key={key}>
          <a
            aria-label={`${label} de ${speaker.name}`}
            className="flex size-11 items-center justify-center rounded-full bg-[hsl(var(--secondary))] text-white focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring"
            href={speaker[key as keyof typeof socialIcons]}
            rel="noopener noreferrer"
            target="_blank"
          >
            <Icon aria-hidden="true" size={20} />
          </a>
        </li>
      ))}
    </ul>
  )
}

function SpeakerPhoto({ speaker }: { speaker?: Speaker }) {
  return (
    <div className="semana-pixel-octagon flex size-20 shrink-0 items-center justify-center bg-white sm:size-24 lg:size-28">
      <div className="semana-pixel-octagon flex size-[68px] items-center justify-center overflow-hidden bg-[hsl(var(--secondary))] text-2xl font-bold text-white sm:size-[84px] lg:size-[100px]">
        {speaker?.photo ? (
          <img alt="" className="size-full object-cover" src={speaker.photo} />
        ) : (
          <span aria-hidden="true">{speaker ? initials(speaker.name) : 'SC'}</span>
        )}
      </div>
    </div>
  )
}

function SponsorBanner({ name }: { name: string }) {
  const sponsor = sponsors.find((item) => item.nome === name)

  return (
    <div className="semana-notch relative z-10 -mb-[3px] w-full bg-white sm:w-[calc(100%+1rem)] px-4 pb-3 pt-2 text-center text-black [--notch:10px]">
      <p className="font-[family-name:var(--font-semana-display)] text-sm font-bold uppercase lg:text-base">
        Palestra patrocinador
      </p>
      {sponsor ? (
        <Image
          alt={sponsor.nome}
          className="mx-auto mt-2 h-10 w-auto object-contain"
          height={sponsor.logo.height}
          src={sponsor.logo.src}
          width={sponsor.logo.width}
        />
      ) : (
        <p className="mt-1 text-lg font-bold uppercase">{name}</p>
      )}
    </div>
  )
}

function ActivityDetails({ activity }: { activity: Activity }) {
  const speakers = activity.speakers.map((speaker) => speaker.name).join(', ')
  const [mainSpeaker] = activity.speakers
  const speakersWithBio = activity.speakers.filter((speaker) => speaker.bio)

  return (
    <>
      <div className="space-y-5 px-5 pb-6 pt-14 sm:px-6">
        <div className="flex items-center gap-4">
          <SpeakerPhoto speaker={mainSpeaker} />
          <div className="min-w-0 space-y-1.5">
            <p className="text-sm font-bold uppercase tracking-wider text-white/80">
              {activityTypeLabels[activity.type]}
            </p>
            <DialogTitle className="text-xl font-bold leading-tight lg:text-2xl">
              {activity.title}
            </DialogTitle>
            <DialogDescription
              className={cn(
                'text-base font-bold text-[hsl(var(--secondary))]',
                !speakers && 'sr-only',
              )}
            >
              {speakers || 'Atividade da Semana da Computação.'}
            </DialogDescription>
            <p className="font-bold">
              {formatTimeRange(activity.startsAt, activity.endsAt)}
            </p>
            {activity.location && (
              <p className="inline-flex items-center gap-1.5 text-sm text-white/80">
                <MapPin aria-hidden="true" size={14} />
                {activity.location}
              </p>
            )}
          </div>
        </div>
        {activity.speakers.length === 1 && <SpeakerSocials speaker={mainSpeaker} />}
      </div>

      <Tabs className="flex flex-1 flex-col" defaultValue="palestra">
        <TabsList className="grid h-auto w-full grid-cols-2 gap-0 rounded-none border-t-[3px] border-white bg-transparent p-0">
          {[
            { value: 'palestra', label: activityTypeLabels[activity.type] },
            { value: 'palestrante', label: 'Palestrante' },
          ].map(({ value, label }) => (
            <TabsTrigger
              className="rounded-none border-0 bg-transparent py-2.5 text-base font-bold uppercase text-[hsl(var(--secondary))] [&+&]:border-l-[3px] [&+&]:border-white data-[state=active]:bg-[hsl(var(--secondary))] data-[state=active]:text-white data-[state=active]:shadow-none"
              disabled={value === 'palestrante' && !activity.speakers.length}
              key={value}
              value={value}
            >
              {label}
            </TabsTrigger>
          ))}
        </TabsList>

        <TabsContent
          className="mt-0 hidden flex-1 flex-col gap-3 border-t-[3px] border-white p-5 data-[state=active]:flex lg:p-7"
          value="palestra"
        >
          <p className="text-white/90 lg:text-lg">
            {activity.description ?? 'Detalhes em breve.'}
          </p>
          {activity.liveUrl && (
            <a
              className="inline-flex items-center gap-2 font-bold underline"
              href={activity.liveUrl}
              rel="noopener noreferrer"
              target="_blank"
            >
              <Youtube aria-hidden="true" size={18} /> Assistir transmissão
              <span className="sr-only"> (abre em nova aba)</span>
            </a>
          )}
        </TabsContent>

        <TabsContent
          className="mt-0 flex-1 space-y-5 border-t-[3px] border-white p-5 lg:p-7"
          value="palestrante"
        >
          {speakersWithBio.length ? (
            speakersWithBio.map((speaker) => (
              <div className="space-y-3" key={speaker.name}>
                {activity.speakers.length > 1 && (
                  <h3 className="text-lg font-bold uppercase leading-tight">
                    {speaker.name}
                  </h3>
                )}
                <p className="text-white/90 lg:text-lg">{speaker.bio}</p>
                {activity.speakers.length > 1 && <SpeakerSocials speaker={speaker} />}
              </div>
            ))
          ) : (
            <p className="text-white/90">Informações sobre o palestrante em breve.</p>
          )}
        </TabsContent>
      </Tabs>

      <div className="flex justify-center px-5 pb-6 pt-2 lg:px-7 lg:pb-7">
        <a
          className="group relative block pb-1.5 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring"
          href={googleCalendarUrl(activity)}
          rel="noopener noreferrer"
          target="_blank"
        >
          <span
            aria-hidden="true"
            className="absolute inset-x-3 bottom-0 h-3 bg-[hsl(var(--secondary))]"
          />
          <span className="semana-notch relative block bg-[hsl(var(--secondary))] p-1.5 [--notch:12px] transition-transform group-hover:-translate-y-0.5">
            <span className="semana-notch block bg-black px-8 py-3 text-lg font-bold uppercase leading-none text-white [--notch:12px] lg:text-xl">
              Salvar na agenda
              <span className="sr-only"> (abre em nova aba)</span>
            </span>
          </span>
        </a>
      </div>
    </>
  )
}

export function ActivityDialog({
  activities,
  index,
  onIndexChange,
}: {
  activities: Activity[]
  index: number | null
  onIndexChange: (index: number | null) => void
}) {
  const activity = index === null ? undefined : activities[index]
  const sponsor = activity?.speakers.find((speaker) => speaker.sponsor)?.sponsor

  return (
    <Dialog
      onOpenChange={(open) => {
        if (!open) onIndexChange(null)
      }}
      open={activity !== undefined}
    >
      <DialogContent
        className={cn(
          'semana-theme flex w-[calc(100%-1rem)] max-w-xl flex-col items-center gap-4 border-0 bg-transparent p-0 font-[family-name:var(--font-semana-body)] text-white shadow-none sm:rounded-none lg:max-w-[38rem] [&>button:last-child]:hidden',
          semanaBody.variable,
          semanaDisplay.variable,
        )}
      >
        {activity && index !== null && (
          <>
            <div className="flex w-full items-center gap-1">
              <button
                aria-label="Atividade anterior"
                className={navButtonClassName}
                disabled={index === 0}
                onClick={() => onIndexChange(index - 1)}
                type="button"
              >
                <PixelChevron className="h-8 w-auto" direction="left" />
              </button>

              <div className="flex min-w-0 flex-1 flex-col items-center">
                {sponsor && <SponsorBanner name={sponsor} />}
                <div className="semana-notch w-full bg-white p-[3px] [--notch:20px]">
                  <div className="semana-notch relative flex max-h-[80svh] flex-col overflow-y-auto bg-[#1c1c1c] [--notch:20px] lg:min-h-[37.5rem]">
                    <DialogClose className="absolute right-5 top-5 z-10 flex size-8 items-center justify-center text-white focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring">
                      <X aria-hidden="true" />
                      <span className="sr-only">Fechar</span>
                    </DialogClose>
                    <ActivityDetails activity={activity} key={index} />
                  </div>
                </div>
              </div>

              <button
                aria-label="Próxima atividade"
                className={navButtonClassName}
                disabled={index === activities.length - 1}
                onClick={() => onIndexChange(index + 1)}
                type="button"
              >
                <PixelChevron className="h-8 w-auto" />
              </button>
            </div>

            {activities.length > 1 && (
              <div className="flex gap-2">
                {activities.map((item, dotIndex) => (
                  <button
                    aria-current={dotIndex === index ? 'true' : undefined}
                    aria-label={`Ir para a atividade ${dotIndex + 1} de ${activities.length}`}
                    className={cn(
                      'size-3 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring',
                      dotIndex === index ? 'bg-[hsl(var(--secondary))]' : 'bg-white',
                    )}
                    key={item.uid}
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
