import { Coffee, MessageCircle, Presentation, Users, Wrench } from 'lucide-react'

import { formatTimeRange } from '../time'
import { type Activity, activityTypeLabels } from '../types'

const typeIcons = {
  talk: Presentation,
  workshop: Wrench,
  conversation: MessageCircle,
  closing: Users,
  coffee_break: Coffee,
}

export function ActivityCard({
  activity,
  onOpen,
}: {
  activity: Activity
  onOpen: () => void
}) {
  const Icon = typeIcons[activity.type]
  const speakers = activity.speakers.map((speaker) => speaker.name).join(', ')
  const photo = activity.speakers.find((speaker) => speaker.photo)?.photo

  return (
    <article className="relative mb-3.5 border-[6px] border-white bg-[hsl(var(--semana-schedule))] after:absolute after:inset-x-2 after:-bottom-5 after:h-3.5 after:bg-[hsl(var(--semana-schedule-ink))]">
      <div className="flex items-center gap-4 p-3 sm:p-4">
        <div className="semana-pixel-octagon flex size-24 shrink-0 items-center justify-center bg-white sm:size-28">
          <div className="flex size-[76px] items-center justify-center overflow-hidden rounded-full bg-[hsl(var(--semana-schedule-ink))] text-white sm:size-[90px]">
            {photo ? (
              <img alt="" className="size-full object-cover" src={photo} />
            ) : (
              <Icon aria-hidden="true" size={36} />
            )}
          </div>
        </div>
        <div className="min-w-0 flex-1">
          <h3 className="text-xl font-semibold leading-tight text-[hsl(var(--semana-schedule-ink))] sm:text-2xl">
            {activity.title}
          </h3>
          <p className="mt-1 text-base font-light text-white sm:text-lg">
            {speakers || activityTypeLabels[activity.type]}
          </p>
        </div>
      </div>

      <div className="flex items-stretch border-t-[6px] border-white">
        <button
          aria-haspopup="dialog"
          className="flex-1 bg-[hsl(var(--semana-schedule-ink))] px-3 py-2 text-center text-base font-semibold uppercase text-white transition-colors hover:bg-[hsl(var(--semana-schedule-ink)/0.85)] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-inset focus-visible:ring-ring sm:text-lg"
          onClick={onOpen}
          type="button"
        >
          Saber mais +<span className="sr-only">: {activity.title}</span>
        </button>
        <p className="flex items-center bg-white px-3 py-2 text-base font-semibold text-[hsl(var(--semana-schedule-ink))] sm:text-lg">
          <span className="sr-only">Horário: </span>
          {formatTimeRange(activity.startsAt, activity.endsAt)}
        </p>
      </div>
    </article>
  )
}
