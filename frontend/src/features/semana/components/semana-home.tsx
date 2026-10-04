import Link from 'next/link'
import Image from 'next/image'

export function SemanaHome() {
  const links = [
    { href: '/semana/cronograma', label: 'Programação' },
    { href: '/semana/cadastro', label: 'Se inscrever' },
  ]

  return (
    <main className="min-h-[calc(100svh-65px)] text-foreground">
      <section className="mx-auto flex min-h-[calc(100svh-65px)] max-w-6xl flex-col items-center justify-center px-6 py-20 text-center">
        <Image
          alt="16ª Semana da Computação"
          className="mb-8 h-auto w-full max-w-xl"
          height={1403}
          priority
          src="/semana/2026/logo-plate.svg"
          width={3412}
        />
        <div className="mt-6 space-y-4">
          <h1 className="font-[family-name:var(--font-semana-display)] text-4xl font-bold uppercase tracking-tight sm:text-7xl">
            16ª Semana da Computação
          </h1>
          <h2 className="font-[family-name:var(--font-semana-display)] text-4xl font-bold uppercase tracking-tight sm:text-7xl">
            Outubro
          </h2>
          <p className="font-[family-name:var(--font-semana-display)] text-3xl font-bold uppercase text-white sm:text-5xl">
            05 a 09
          </p>
          <p className="font-[family-name:var(--font-semana-display)] text-2xl font-bold uppercase sm:text-4xl">
            12h - 18h
          </p>
        </div>
        <p className="mt-8 max-w-xl text-lg text-white/75 sm:text-xl">
          Evento da SymComp no IME-USP para estudantes, pesquisadores e profissionais
          celebrarem a computação. O site reúne programação, inscrições, desafios e
          presença na Semana da Computação.
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
