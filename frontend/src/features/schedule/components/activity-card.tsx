import {
  CalendarPlus,
  Clock,
  Coffee,
  MapPin,
  MessageCircle,
  Presentation,
  Users,
  Youtube,
} from 'lucide-react'

import { SemanaButton } from '@/features/semana/components/semana-button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'

import { googleCalendarUrl } from '../calendar'
import type { Activity, ActivityType } from '../types'

const typeLabels: Record<ActivityType, string> = {
  talk: 'Palestra',
  conversation: 'Conversa',
  closing: 'Encerramento',
  coffee_break: 'Intervalo',
}

const typeIcons = {
  talk: Presentation,
  conversation: MessageCircle,
  closing: Users,
  coffee_break: Coffee,
}

const timeFormatter = new Intl.DateTimeFormat('pt-BR', {
  hour: '2-digit',
  minute: '2-digit',
  timeZone: 'America/Sao_Paulo',
})

export function ActivityCard({ activity }: { activity: Activity }) {
  const Icon = typeIcons[activity.type]
  const speakers = activity.speakers.map((speaker) => speaker.name).join(', ')

  return (
    <article className="rounded-none border-[7px] border-white bg-card p-5 text-card-foreground shadow-[0_8px_0_hsl(var(--semana-contrast))]">
      <div className="flex items-start gap-4">
        <div className="rounded-none border-2 border-[hsl(var(--semana-contrast))] bg-primary p-2.5">
          <Icon aria-hidden="true" size={22} />
        </div>
        <div className="min-w-0 flex-1 space-y-3">
          <div>
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
              {typeLabels[activity.type]}
            </p>
            <h3 className="mt-1 text-xl font-semibold leading-tight">{activity.title}</h3>
          </div>
          <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm text-muted-foreground">
            <span className="inline-flex items-center gap-1.5">
              <Clock aria-hidden="true" size={16} />
              {timeFormatter.format(new Date(activity.startsAt))}–
              {timeFormatter.format(new Date(activity.endsAt))}
            </span>
            {activity.location && (
              <span className="inline-flex items-center gap-1.5">
                <MapPin aria-hidden="true" size={16} />
                {activity.location}
              </span>
            )}
          </div>
          {speakers && <p className="text-sm font-medium">{speakers}</p>}
          {activity.description && (
            <p className="text-sm leading-6 text-muted-foreground">
              {activity.description}
            </p>
          )}
          {activity.liveUrl && (
            <a
              className="inline-flex items-center gap-2 text-sm font-semibold underline"
              href={activity.liveUrl}
              rel="noreferrer"
              target="_blank"
            >
              <Youtube aria-hidden="true" size={16} /> Assistir transmissão
            </a>
          )}
          <div className="flex flex-wrap gap-3">
            <SemanaButton
              asChild
              className="border-4 px-3 py-2 text-xs shadow-[0_4px_0_hsl(var(--semana-contrast))]"
            >
              <a href={googleCalendarUrl(activity)} rel="noreferrer" target="_blank">
                <CalendarPlus aria-hidden="true" className="mr-2" size={16} /> Adicionar à
                agenda
              </a>
            </SemanaButton>
            {(activity.description ||
              activity.speakers.some((speaker) => speaker.bio || speaker.photo)) && (
              <Dialog>
                <DialogTrigger asChild>
                  <SemanaButton className="border-4 px-3 py-2 text-xs" variant="outline">
                    Saber mais
                  </SemanaButton>
                </DialogTrigger>
                <DialogContent className="semana-theme">
                  <DialogHeader>
                    <DialogTitle>{activity.title}</DialogTitle>
                    <DialogDescription>
                      {activity.speakers.map((speaker) => speaker.name).join(', ')}
                    </DialogDescription>
                  </DialogHeader>
                  {activity.description && (
                    <p className="text-sm leading-6">{activity.description}</p>
                  )}
                  <div className="space-y-3">
                    {activity.speakers.map(
                      (speaker) =>
                        (speaker.bio || speaker.photo) && (
                          <div className="flex gap-3" key={speaker.name}>
                            {speaker.photo && (
                              <img
                                alt=""
                                className="size-12 rounded-full object-cover"
                                src={speaker.photo}
                              />
                            )}
                            <div>
                              <h3 className="font-semibold">{speaker.name}</h3>
                              {speaker.bio && (
                                <p className="text-sm text-muted-foreground">
                                  {speaker.bio}
                                </p>
                              )}
                            </div>
                          </div>
                        ),
                    )}
                  </div>
                </DialogContent>
              </Dialog>
            )}
          </div>
        </div>
      </div>
    </article>
  )
}
