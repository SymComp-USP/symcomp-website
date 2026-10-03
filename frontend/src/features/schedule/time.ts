const timeFormatter = new Intl.DateTimeFormat('pt-BR', {
  hour: '2-digit',
  minute: '2-digit',
  timeZone: 'America/Sao_Paulo',
})

function formatTime(date: string) {
  const parts = timeFormatter.formatToParts(new Date(date))
  const part = (type: Intl.DateTimeFormatPartTypes) =>
    parts.find((item) => item.type === type)?.value ?? '00'
  return `${part('hour')}h${part('minute')}`
}

// "12h30 - 13h00" in Brasília time.
export function formatTimeRange(startsAt: string, endsAt: string) {
  return `${formatTime(startsAt)} - ${formatTime(endsAt)}`
}
