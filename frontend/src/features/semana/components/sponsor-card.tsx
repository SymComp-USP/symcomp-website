import type { Sponsor } from '../sponsors'
import { SponsorDialog } from './sponsor-dialog'
import { SponsorLogo } from './sponsor-logo'

export function SponsorCard({ sponsor }: { sponsor: Sponsor }) {
  return (
    <article className="relative w-full max-w-sm pt-3">
      {sponsor.cota && (
        <p className="absolute right-0 top-0 z-10 border-4 border-[hsl(var(--semana-contrast))] bg-primary px-2 py-1 font-[family-name:var(--font-semana-display)] text-xs font-bold uppercase text-primary-foreground">
          <span className="sr-only">Cota </span>
          {sponsor.cota}
        </p>
      )}

      <div className="border-[7px] border-white bg-card text-card-foreground shadow-[0_8px_0_hsl(var(--semana-contrast))]">
        <div className="flex flex-col items-center gap-5 p-6">
          <SponsorLogo sponsor={sponsor} />
          <h2 className="text-center font-[family-name:var(--font-semana-display)] text-xl font-bold uppercase">
            {sponsor.nome}
          </h2>
        </div>
        <div className="flex justify-center border-t-[7px] border-white bg-[hsl(var(--semana-sponsor-soft))] p-3">
          <SponsorDialog sponsor={sponsor} />
        </div>
      </div>
    </article>
  )
}
