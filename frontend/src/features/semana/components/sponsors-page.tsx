import { sponsors } from '../sponsors'
import { SponsorCard } from './sponsor-card'
import { SponsorsCarousel } from './sponsors-carousel'

export function SponsorsPage() {
  return (
    <main className="min-h-[calc(100svh-65px)] bg-[hsl(var(--semana-sponsor))] text-white">
      <div className="mx-auto max-w-4xl px-6 py-16">
        <div className="mb-10 space-y-3 text-center">
          <h1 className="font-[family-name:var(--font-semana-display)] text-2xl font-bold uppercase tracking-tight sm:text-5xl">
            Patrocinadores
          </h1>
          <p className="text-xl text-white/90">
            Conheça as empresas patrocinadoras do evento!
          </p>
        </div>

        {sponsors.length ? (
          <SponsorsCarousel>
            {sponsors.map((sponsor) => (
              <SponsorCard key={sponsor.nome} sponsor={sponsor} />
            ))}
          </SponsorsCarousel>
        ) : (
          <p className="text-center text-lg">Patrocinadores em breve.</p>
        )}
      </div>
    </main>
  )
}
