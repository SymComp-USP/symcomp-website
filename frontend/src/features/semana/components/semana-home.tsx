import Link from 'next/link'

export function SemanaHome() {
  const links = [
    { href: '/semana/cronograma', label: 'Programação' },
    { href: '/semana/cadastro', label: 'Se inscrever' },
  ]

  return (
    <main className="min-h-[calc(100svh-65px)] bg-background text-foreground">
      <section className="mx-auto flex min-h-[calc(100svh-65px)] max-w-6xl flex-col items-center justify-center px-6 py-20 text-center">
        <p className="max-w-full font-[family-name:var(--font-semana-display)] text-3xl font-bold uppercase leading-tight tracking-[0.1em] text-primary sm:text-6xl sm:tracking-[0.25em]">
          Semana da Computação 2026
        </p>
        <div className="mt-6 space-y-4">
          <h1 className="font-[family-name:var(--font-semana-display)] text-4xl font-bold uppercase tracking-tight sm:text-7xl">
            Outubro
          </h1>
          <p className="font-[family-name:var(--font-semana-display)] text-3xl font-bold uppercase text-primary sm:text-5xl">
            05 à 09
          </p>
          <p className="font-[family-name:var(--font-semana-display)] text-2xl font-bold uppercase sm:text-4xl">
            12h - 18h
          </p>
        </div>
        <p className="mt-8 max-w-xl text-lg text-white/75 sm:text-xl">
          Um encontro de estudantes, pesquisadores e profissionais para celebrar a
          computação no IME-USP.
        </p>
        <nav
          aria-label="Páginas da Semana da Computação"
          className="mt-10 flex flex-wrap justify-center gap-3"
        >
          {links.map((link) => (
            <Link
              className="rounded-full border-4 border-[hsl(var(--semana-contrast))] bg-white px-5 py-3 font-[family-name:var(--font-semana-display)] text-sm font-bold uppercase text-[hsl(var(--semana-contrast))] shadow-[0_4px_0_hsl(var(--semana-contrast))] transition-transform hover:-translate-y-0.5 hover:bg-[hsl(var(--semana-accent))] active:translate-y-1 active:shadow-[0_2px_0_hsl(var(--semana-contrast))]"
              href={link.href}
              key={link.href}
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </section>
    </main>
  )
}
