export type ActivityType = 'talk' | 'conversation' | 'closing' | 'coffee_break'

export type Speaker = {
  name: string
  bio?: string
  photo?: string
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
