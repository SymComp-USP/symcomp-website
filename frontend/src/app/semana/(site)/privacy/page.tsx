import type { Metadata } from 'next'
import Script from 'next/script'

export const metadata: Metadata = {
  title: 'Política de Privacidade | Semana da Computação',
  description: 'Política de privacidade da Semana da Computação.',
}

export default function PrivacyPage() {
  return (
    <main className="mx-auto w-full max-w-4xl px-6 py-12 sm:py-16">
      <Script src="https://cdn.iubenda.com/iubenda.js" strategy="afterInteractive" />
      <article className="space-y-6 rounded-none border-[6px] border-[hsl(var(--semana-contrast))] bg-card p-6 text-card-foreground sm:p-10">
        <header className="space-y-3">
          <h1 className="font-[family-name:var(--font-semana-display)] text-4xl uppercase sm:text-5xl">
            Política de privacidade
          </h1>
          <p className="text-muted-foreground">
            Consulte abaixo nossa política de privacidade e controles de cookies.
          </p>
        </header>
        <div className="flex flex-wrap gap-3">
          <a
            className="iubenda-white iubenda-noiframe iubenda-embed"
            href="https://www.iubenda.com/privacy-policy/40876019"
            title="Política de Privacidade"
          >
            Política de Privacidade
          </a>
          <a
            className="iubenda-white iubenda-noiframe iubenda-embed"
            href="https://www.iubenda.com/privacy-policy/40876019/cookie-policy"
            title="Política de Cookies"
          >
            Política de Cookies
          </a>
        </div>
      </article>
    </main>
  )
}
