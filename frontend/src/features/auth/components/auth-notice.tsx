import type { ReactNode } from 'react'

export function AuthNotice({
  children,
  variant = 'success',
}: {
  children: ReactNode
  variant?: 'error' | 'success'
}) {
  const error = variant === 'error'

  return (
    <div
      aria-live="polite"
      className={`border-[8px] border-[hsl(var(--semana-contrast))] bg-white px-6 py-4 text-center font-[family-name:var(--font-semana-display)] text-lg font-bold uppercase text-[hsl(var(--semana-contrast))] shadow-[0_8px_0_hsl(var(--semana-contrast))] ${error ? 'text-destructive' : ''}`}
      role={error ? 'alert' : 'status'}
    >
      {children}
    </div>
  )
}
