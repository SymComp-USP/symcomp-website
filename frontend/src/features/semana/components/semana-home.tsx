import Image from 'next/image'
import Link from 'next/link'

export function SemanaHome() {
  const links = [
    { href: '/semana/cronograma', label: 'Cronograma' },
    { href: '/semana/cadastro', label: 'Se inscrever' },
  ]

  return (
    <main className="min-h-[calc(100svh-65px)] overflow-x-clip bg-background text-foreground">
      <section className="mx-auto grid min-h-[calc(100svh-65px)] max-w-6xl items-center gap-10 px-6 py-10 md:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] md:py-20">
        <div className="flex flex-col items-center text-center">
          <p className="max-w-full font-[family-name:var(--font-semana-display)] text-2xl font-bold uppercase leading-tight tracking-[0.08em] text-primary sm:text-4xl sm:tracking-[0.15em] md:text-4xl lg:text-5xl">
            Semana da Computação 2026
          </p>
          {/* On phones the dates sit on the right with the mascot peeking in from
              the left edge, behind the text; from md up the mascot gets its
              own column, on the left. */}
          <div className="relative mt-6 flex min-h-72 w-full items-center justify-end sm:min-h-96 md:mt-6 md:block md:min-h-0">
            <Image
              alt=""
              aria-hidden="true"
              className="pointer-events-none absolute -left-20 top-1/2 h-auto w-72 max-w-none -translate-y-1/2 [image-rendering:pixelated] sm:-left-24 sm:w-96 md:hidden"
              height={3000}
              priority
              sizes="(min-width: 640px) 384px, 288px"
              src="/semana/2026/symcompinho_e_dino.png"
              width={3000}
            />
            <div className="relative space-y-3 text-right md:space-y-4 md:text-center">
              <h1 className="font-[family-name:var(--font-semana-display)] text-3xl font-bold uppercase tracking-tight sm:text-5xl md:text-6xl lg:text-7xl">
                Outubro
              </h1>
              <p className="font-[family-name:var(--font-semana-display)] text-2xl font-bold uppercase text-primary sm:text-4xl md:text-4xl lg:text-5xl">
                05 à 09
              </p>
              <p className="font-[family-name:var(--font-semana-display)] text-xl font-bold uppercase sm:text-3xl md:text-3xl lg:text-4xl">
                12h - 18h
              </p>
            </div>
          </div>
          <p className="mt-6 max-w-xl text-lg text-white/75 sm:text-xl md:mt-8">
            Um encontro de estudantes, pesquisadores e profissionais para celebrar a
            computação no IME-USP.
          </p>
          <nav
            aria-label="Páginas da Semana da Computação"
            className="mt-10 flex flex-wrap justify-center gap-3"
          >
            {links.map((link) => (
              <Link
                className="rounded-full border-4 border-[hsl(var(--semana-contrast))] bg-white px-5 py-3 font-[family-name:var(--font-semana-display)] text-sm font-bold uppercase text-[hsl(var(--semana-contrast))] shadow-[0_4px_0_hsl(var(--semana-contrast))] transition-transform hover:-translate-y-0.5 hover:bg-[hsl(var(--semana-hover))] active:translate-y-1 active:shadow-[0_2px_0_hsl(var(--semana-contrast))]"
                href={link.href}
                key={link.href}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>

        <div className="hidden md:order-first md:flex md:justify-end">
          <Image
            alt="Symcompinho, mascote da SymComp, montado em um dinossauro"
            className="h-auto w-[125%] max-w-none shrink-0 [image-rendering:pixelated] lg:w-[130%]"
            height={3000}
            priority
            sizes="(min-width: 1024px) 700px, 64vw"
            src="/semana/2026/symcompinho_e_dino.png"
            width={3000}
          />
        </div>
      </section>
    </main>
  )
}
