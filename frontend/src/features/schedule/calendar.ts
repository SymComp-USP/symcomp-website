import type { Activity } from './types'

function calendarDate(value: string) {
  return new Date(value)
    .toISOString()
    .replace(/[-:]/g, '')
    .replace(/\.\d{3}Z$/, 'Z')
}

export function googleCalendarUrl(activity: Activity) {
  const url = new URL('https://calendar.google.com/calendar/render')
  url.searchParams.set('action', 'TEMPLATE')
  url.searchParams.set('text', activity.title)
  url.searchParams.set(
    'dates',
    `${calendarDate(activity.startsAt)}/${calendarDate(activity.endsAt)}`,
  )
  if (activity.description) url.searchParams.set('details', activity.description)
  if (activity.location) url.searchParams.set('location', activity.location)
  return url.toString()
}
