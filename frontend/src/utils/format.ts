export function formatDuration(totalMinutes: number): string {
  const minutes = Math.max(0, Math.round(totalMinutes))
  const hours = Math.floor(minutes / 60)
  const rest = minutes % 60
  if (hours === 0) return `${rest} min`
  return rest === 0 ? `${hours}h` : `${hours}h ${rest}m`
}

export function getInitials(fullname?: string | null): string {
  const parts = (fullname ?? '').trim().split(/\s+/).filter(Boolean)
  if (parts.length === 0) return '?'
  const [first = '', ...rest] = parts
  const last = rest[rest.length - 1] ?? ''
  return (first.charAt(0) + last.charAt(0)).toUpperCase()
}

export function getGreeting(date: Date): string {
  const hour = date.getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 18) return 'Good afternoon'
  return 'Good evening'
}
