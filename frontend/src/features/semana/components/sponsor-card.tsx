import type { Sponsor } from '../sponsors'
import { SponsorLogo } from './sponsor-logo'

export function SponsorCard({
  sponsor,
  onOpen,
}: {
  sponsor: Sponsor
  onOpen: () => void
}) {
  return (
    <article className="relative w-full max-w-[15rem] border-x-4 lg:max-w-[22rem] border-t-4 border-white bg-[hsl(var(--semana-sponsor-soft))]">
      {sponsor.cota && (
        <p className="absolute -right-10 top-2 z-10 border-4 border-white bg-[hsl(var(--semana-contrast))] px-4 py-0.5 text-base font-bold lg:text-lg uppercase text-white">
          <span className="sr-only">Cota </span>
          {sponsor.cota}
        </p>
      )}

      <div className="flex flex-col items-center gap-4 px-3 pb-5 pt-6 lg:gap-8 lg:pb-10 lg:pt-12">
        <SponsorLogo
          className="aspect-square size-auto w-3/4 max-w-40 lg:max-w-60"
          sponsor={sponsor}
        />
        <h2 className="text-center text-xl font-bold uppercase leading-tight lg:text-2xl">
          {sponsor.nome}
        </h2>
      </div>

      <button
        className="-mx-1 block w-[calc(100%+0.5rem)] border-4 border-white bg-[hsl(var(--semana-contrast))] px-3 py-2 text-base font-bold uppercase text-white hover:underline lg:py-3 lg:text-lg focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring"
        onClick={onOpen}
        type="button"
      >
        Saber mais +<span className="sr-only"> sobre {sponsor.nome}</span>
      </button>
      <div
        aria-hidden="true"
        className="absolute inset-x-0 top-full h-1.5 bg-[hsl(var(--semana-contrast))]"
      />
    </article>
  )
}
