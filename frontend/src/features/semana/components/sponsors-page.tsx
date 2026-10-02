import { sponsors } from '../sponsors'
import { SponsorsShowcase } from './sponsors-showcase'

export function SponsorsPage() {
  return (
    <main className="min-h-full overflow-x-clip bg-[hsl(var(--semana-sponsor))] text-white">
      <div className="mx-auto max-w-5xl px-4 py-16 sm:px-6 lg:max-w-none">
        <div className="mb-10 space-y-3 text-center">
          <h1 className="font-[family-name:var(--font-semana-display)] text-2xl font-bold uppercase tracking-tight sm:text-5xl">
            Patrocinadores
          </h1>
          <p className="mx-auto max-w-md text-lg text-white/90">
            Conheça as empresas patrocinadoras e participantes do evento!
          </p>
        </div>

        {sponsors.length ? (
          <SponsorsShowcase sponsors={sponsors} />
        ) : (
          <p className="text-center text-lg">Patrocinadores em breve.</p>
        )}
      </div>
    </main>
  )
}
