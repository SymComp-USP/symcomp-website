import { requestApi } from '@/features/auth/api'
import type { Semana } from '@/features/semana/api'

import type { Activity } from './types'

type ApiActivity = {
  id: string
  tipo: 'palestra' | 'workshop' | 'encerramento' | 'conversa' | 'coffee_break'
  titulo: string
  descricao: string | null
  local: string | null
  palestrantes: { nome: string; sobre?: string; foto?: string }[]
  comeca_as: string
  termina_as: string
  link_live: string | null
}

export function listScheduleWeeks() {
  return requestApi<Semana[]>('/semanas')
}

export function listScheduleActivities(semanaId: number) {
  return requestApi<ApiActivity[]>(`/semanas/${semanaId}/atividades`)
}

function mediaUrl(path: string) {
  if (path.startsWith('http')) return path
  return `${process.env.NEXT_PUBLIC_API_URL ?? ''}${path}`
}

export function mapActivity(activity: ApiActivity) {
  const typeByActivity: Record<ApiActivity['tipo'], Activity['type']> = {
    palestra: 'talk',
    workshop: 'talk',
    encerramento: 'closing',
    conversa: 'conversation',
    coffee_break: 'coffee_break',
  }

  return {
    uid: activity.id,
    type: typeByActivity[activity.tipo],
    title: activity.titulo,
    description: activity.descricao ?? undefined,
    speakers: activity.palestrantes.map((speaker) => ({
      name: speaker.nome,
      bio: speaker.sobre,
      photo: speaker.foto ? mediaUrl(speaker.foto) : undefined,
    })),
    startsAt: activity.comeca_as,
    endsAt: activity.termina_as,
    location: activity.local ?? undefined,
    liveUrl: activity.link_live ?? undefined,
  } as const
}
