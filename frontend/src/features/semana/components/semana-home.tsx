import Link from 'next/link'

import { SemanaButton } from './semana-button'

export function SemanaHome() {
  return (
    <main className="min-h-[calc(100svh-65px)] bg-background text-foreground">
      <section className="mx-auto flex min-h-[calc(100svh-65px)] max-w-6xl flex-col justify-center gap-8 px-6 py-20">
        <p className="font-[family-name:var(--font-semana-display)] text-sm font-bold uppercase tracking-[0.2em] text-primary">
          Próxima edição
        </p>
        <div className="max-w-3xl space-y-6">
          <h1 className="font-[family-name:var(--font-semana-display)] text-4xl font-bold uppercase tracking-tight sm:text-6xl">
            Semana da Computação 2026
          </h1>
          <p className="max-w-2xl text-xl leading-8 text-white/80 sm:text-2xl">
            Uma nova edição da Semana da Computação está em construção. Em breve,
            divulgaremos as datas, a programação e as inscrições do evento.
          </p>
        </div>
        <SemanaButton asChild>
          <Link href="/semana/login">Entrar</Link>
        </SemanaButton>
      </section>
    </main>
  )
}
