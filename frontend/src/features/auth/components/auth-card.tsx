import Link from 'next/link'
import type { ReactNode } from 'react'

export function AuthCard({
  title,
  description,
  children,
  footer,
}: {
  title: string
  description: string
  children: ReactNode
  footer: { text: string; label: string; href: string }
}) {
  return (
    <main className="mx-auto flex min-h-[calc(100svh-65px)] max-w-6xl items-start justify-center px-6 py-10 sm:py-16">
      <section className="w-full max-w-md space-y-8 text-foreground">
        <div className="space-y-2 text-center">
          <h1 className="font-[family-name:var(--font-semana-display)] text-4xl font-bold uppercase tracking-tight">
            {title}
          </h1>
          <p className="mx-auto max-w-xs font-[family-name:var(--font-semana-body)] text-lg text-foreground">
            {description}
          </p>
        </div>
        {children}
        <p className="text-center text-sm text-foreground">
          {footer.text}{' '}
          <Link
            className="font-medium text-foreground underline underline-offset-4"
            href={footer.href}
          >
            {footer.label}
          </Link>
        </p>
      </section>
    </main>
  )
}
