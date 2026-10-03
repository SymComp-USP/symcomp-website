import { BsInstagram, BsLinkedin, BsYoutube } from 'react-icons/bs'

import { SymcompLogo } from './symcomp-logo'

const socialLinks = [
  {
    label: 'Instagram da SymComp',
    href: 'https://www.instagram.com/symcomp.imeusp/',
    icon: BsInstagram,
  },
  {
    label: 'LinkedIn da SymComp',
    href: 'https://www.linkedin.com/company/symcompimeusp',
    icon: BsLinkedin,
  },
  {
    label: 'Canal da Semana da Computação no YouTube',
    href: 'https://www.youtube.com/@semanadacomputacaoime-usp',
    icon: BsYoutube,
  },
]

export function AboutPage() {
  return (
    <main className="mx-auto min-h-[calc(100svh-65px)] max-w-4xl px-6 py-16">
      <div className="mx-auto flex max-w-2xl flex-col items-center text-center">
        <h1 className="font-[family-name:var(--font-semana-display)] text-4xl font-bold uppercase tracking-tight sm:text-5xl">
          Quem somos?
        </h1>
        <p className="mt-4 text-xl text-white/80">
          Conheça o grupo de extensão SymComp, responsável pela 16ª Semana da Computação.
        </p>

        <SymcompLogo
          aria-label="Identidade visual da SymComp"
          className="mt-10 size-40 text-white sm:size-48"
          role="img"
        />

        <h2 className="mt-10 font-[family-name:var(--font-semana-display)] text-3xl font-bold uppercase text-primary">
          SymComp
        </h2>
        <p className="mt-4 text-lg text-white/80 sm:text-xl">
          Somos um grupo de extensão do Instituto de Matemática e Estatística da USP
          formado por alunos da graduação. Nossa missão é disseminar a computação para a
          comunidade externa e interna da universidade. Venha fazer parte do grupo também!
        </p>

        <ul aria-label="Redes sociais da SymComp" className="mt-8 flex gap-4">
          {socialLinks.map(({ label, href, icon: Icon }) => (
            <li key={label}>
              <a
                aria-label={label}
                className="flex size-12 items-center justify-center rounded-full border-4 border-[hsl(var(--semana-contrast))] bg-white text-[hsl(var(--semana-contrast))] shadow-[0_4px_0_hsl(var(--semana-contrast))] transition-transform hover:-translate-y-0.5 hover:bg-[hsl(var(--semana-hover))] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring active:translate-y-1 active:shadow-[0_2px_0_hsl(var(--semana-contrast))]"
                href={href}
                rel="noopener noreferrer"
                target="_blank"
              >
                <Icon aria-hidden="true" size={22} />
              </a>
            </li>
          ))}
        </ul>
      </div>
    </main>
  )
}
