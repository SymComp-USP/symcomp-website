import type { Metadata } from 'next'

import { PrivacyPolicyContent } from './privacy-policy-content'

export const metadata: Metadata = {
  title: 'Política de Privacidade | 16ª Semana da Computação',
  description:
    'Como a 16ª Semana da Computação trata dados de cadastro, login com Google e participação no evento.',
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
      </article>
    </main>
  )
}
