import Image from 'next/image'
import Link from 'next/link'

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

const sectionTitle =
  'mb-5 border-b-[6px] border-[hsl(var(--semana-contrast))] pb-3 font-[family-name:var(--font-semana-display)] text-2xl font-bold uppercase'

export function AboutPage() {
  return (
    <main className="mx-auto min-h-[calc(100svh-65px)] max-w-4xl px-6 py-16">
      <div className="mb-12 max-w-2xl space-y-3">
        <p className="font-[family-name:var(--font-semana-display)] text-sm font-bold uppercase tracking-[0.2em] text-primary">
          Semana da Computação
        </p>
        <h1 className="font-[family-name:var(--font-semana-display)] text-4xl font-bold uppercase tracking-tight sm:text-5xl">
          Sobre nós
        </h1>
        <p className="text-xl text-white/80">
          Organizando eventos sobre computação, aproximando a comunidade interna e externa
          do curso de Bacharelado em Ciência da Computação da USP Butantã.
        </p>
      </div>

      <div className="space-y-12">
        <section aria-labelledby="quem-somos">
          <h2 className={sectionTitle} id="quem-somos">
            Quem somos
          </h2>
          <p className="text-lg text-white/80">
            A SymComp, Simpósio da Computação, é um grupo de extensão originado em 2023 a
            partir da comissão responsável pela Semana da Computação do Instituto de
            Matemática e Estatística da Universidade de São Paulo (IME USP). O grupo
            surgiu com o propósito de fortalecer a presença do curso de Ciência da
            Computação não apenas dentro da comunidade uspiana, mas também na comunidade
            externa, promovendo eventos e atividades relacionadas a essa ciência tão
            essencial e relevante na atualidade.
          </p>
        </section>

        <section aria-labelledby="a-semana">
          <h2 className={sectionTitle} id="a-semana">
            A Semana da Computação
          </h2>
          <div className="space-y-4 text-lg text-white/80">
            <p>
              A Semana da Computação do IME USP é um dos maiores eventos estudantis de
              tecnologia e inovação do Brasil. Organizada por alunos do Instituto de
              Matemática e Estatística da Universidade de São Paulo, reúne palestras,
              workshops, minicursos e painéis sobre ciência da computação, inteligência
              artificial, segurança da informação, desenvolvimento de software, design de
              sistemas e carreira em tecnologia.
            </p>
            <p>
              O evento conecta estudantes, pesquisadores e profissionais da área,
              promovendo troca de conhecimento, networking e contato direto com as
              tendências mais atuais do mercado.
            </p>
          </div>
        </section>

        <section aria-labelledby="nossos-projetos">
          <h2 className={sectionTitle} id="nossos-projetos">
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
                >
                  Conhecer
                </Link>
              </article>
            ))}
          </div>
        </section>
      </div>
    </main>
  )
}
