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
    <article className="relative w-full max-w-[15rem] pt-3">
      {sponsor.cota && (
        <p className="absolute -right-3 top-0 z-10 border-4 border-white bg-[hsl(var(--semana-contrast))] px-2 py-1 text-sm font-bold uppercase text-white">
          <span className="sr-only">Cota </span>
          {sponsor.cota}
        </p>
      )}

      <div className="border-4 border-white bg-[hsl(var(--semana-sponsor-soft))]">
        <div className="flex flex-col items-center gap-5 px-4 pb-5 pt-8">
          <SponsorLogo className="size-36" sponsor={sponsor} />
          <h2 className="text-center text-xl font-bold uppercase leading-tight">
            {sponsor.nome}
          </h2>
        </div>
        <button
          className="block w-full border-t-4 border-white bg-[hsl(var(--semana-contrast))] px-3 py-2 text-base font-bold uppercase text-white hover:underline focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-inset focus-visible:ring-ring"
          onClick={onOpen}
          type="button"
        >
          Saber mais +<span className="sr-only"> sobre {sponsor.nome}</span>
        </button>
      </div>
    </article>
  )
}
