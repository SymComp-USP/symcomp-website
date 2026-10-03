import Image from 'next/image'
import Link from 'next/link'
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

const projects = [
  {
    label: 'Semana da Computação',
    href: '/semana',
    imageUrl: '/logo/sc.png',
    imageWidth: 1080,
    imageHeight: 1080,
    description:
      'Anualmente reunimos alunos da graduação e visitantes para participar de uma semana de palestras, competições, brindes, networking e coffee breaks.',
  },
  {
    label: 'ByteCafé',
    href: '/bytecafe',
    imageUrl: '/logo/bc.png',
    imageWidth: 477,
    imageHeight: 592,
    description:
      'Duas vezes por semestre convidamos alunos do Ensino Médio para conhecer a USP e o curso de Ciência da Computação.',
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

      <section aria-labelledby="nossos-projetos" className="mt-20">
        <h2
          className="mb-5 border-b-[6px] border-[hsl(var(--semana-contrast))] pb-3 font-[family-name:var(--font-semana-display)] text-2xl font-bold uppercase"
          id="nossos-projetos"
        >
          Nossos projetos
        </h2>
        <div className="grid gap-6 md:grid-cols-2">
          {projects.map((project) => (
            <article
              className="flex flex-col gap-4 rounded-none border-[7px] border-white bg-card p-5 text-card-foreground shadow-[0_8px_0_hsl(var(--semana-contrast))]"
              key={project.href}
            >
              <div className="flex h-32 items-center justify-center bg-[hsl(var(--semana-accent))] p-4">
                <Image
                  alt={`Logo ${project.label}`}
                  className="h-full w-auto object-contain"
                  height={project.imageHeight}
                  src={project.imageUrl}
                  width={project.imageWidth}
                />
              </div>
              <h3 className="font-[family-name:var(--font-semana-display)] text-xl font-bold uppercase">
                {project.label}
              </h3>
              <p className="flex-1 text-muted-foreground">{project.description}</p>
              <Link
                className="w-fit border-4 border-[hsl(var(--semana-contrast))] bg-primary px-4 py-2 font-[family-name:var(--font-semana-display)] text-sm font-bold uppercase text-primary-foreground shadow-[0_4px_0_hsl(var(--semana-contrast))] transition-transform hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring active:translate-y-1 active:shadow-[0_2px_0_hsl(var(--semana-contrast))]"
                href={project.href}
                rel="noopener noreferrer"
                target="_blank"
              >
                Conhecer
                <span className="sr-only"> {project.label} (abre em nova aba)</span>
              </Link>
            </article>
          ))}
        </div>
      </section>
    </main>
  )
}
