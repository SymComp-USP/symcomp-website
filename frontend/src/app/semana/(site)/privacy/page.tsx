import type { Metadata } from 'next'

import { PrivacyPolicyContent } from './privacy-policy-content'

export const metadata: Metadata = {
  title: 'Política de Privacidade | Semana da Computação',
  description: 'Política de privacidade da Semana da Computação.',
}

export default function PrivacyPage() {
  return (
    <main className="mx-auto w-full max-w-4xl px-6 py-12 sm:py-16">
      <article className="space-y-6 rounded-none border-[6px] border-[hsl(var(--semana-contrast))] bg-card p-6 text-card-foreground sm:p-10">
        <header className="space-y-3">
          <h1 className="font-[family-name:var(--font-semana-display)] text-4xl uppercase sm:text-5xl">
            Política de privacidade
          </h1>
          <p className="text-muted-foreground">
            Última atualização: 4 de outubro de 2026.
          </p>
        </header>
        <PrivacyPolicyContent />
        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">
            Política completa hospedada pela iubenda
          </h2>
          <p>
            A política completa de privacidade está disponível abaixo. Ela também descreve
            o uso de cookies e como alterações nesta política são comunicadas.
          </p>
          <iframe
            className="h-[70rem] w-full border-0"
            src="https://www.iubenda.com/privacy-policy/40876019"
            title="Política de Privacidade"
          />
          <p className="text-sm text-muted-foreground">
            Se a política não aparecer, abra{' '}
            <a
              className="underline underline-offset-4"
              href="https://www.iubenda.com/privacy-policy/40876019"
            >
              Política de Privacidade
            </a>
            .
          </p>
        </section>
        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">Política de Cookies completa</h2>
          <p>A Política de Cookies completa também está disponível abaixo.</p>
          <iframe
            className="h-[34rem] w-full border-0"
            src="https://www.iubenda.com/privacy-policy/40876019/cookie-policy"
            title="Política de Cookies"
          />
          <p className="text-sm text-muted-foreground">
            Se não aparecer, abra{' '}
            <a
              className="underline underline-offset-4"
              href="https://www.iubenda.com/privacy-policy/40876019/cookie-policy"
            >
              Política de Cookies
            </a>
            .
          </p>
        </section>
      </article>
    </main>
  )
}
