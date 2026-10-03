export type ActivityType =
  'talk' | 'workshop' | 'conversation' | 'closing' | 'coffee_break'

export const activityTypeLabels: Record<ActivityType, string> = {
  talk: 'Palestra',
  workshop: 'Oficina',
  conversation: 'Conversa',
  closing: 'Encerramento',
  coffee_break: 'Intervalo',
}

export type Speaker = {
  name: string
  bio?: string
  photo?: string
  linkedin?: string
  youtube?: string
  instagram?: string
  // Sponsor name as listed in features/semana/sponsors.ts.
  sponsor?: string
}

export type Activity = {
  uid: string
  type: ActivityType
  title: string
  description?: string
  speakers: Speaker[]
  startsAt: string
  endsAt: string
  location?: string
  liveUrl?: string
}
