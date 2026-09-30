'use client'

import Image from 'next/image'
import { useState } from 'react'

import type { Sponsor } from '../sponsors'
import { SponsorCard } from './sponsor-card'
import { SponsorDialog } from './sponsor-dialog'
import { SponsorsCarousel } from './sponsors-carousel'

export function SponsorsShowcase({ sponsors }: { sponsors: Sponsor[] }) {
  const [openIndex, setOpenIndex] = useState<number | null>(null)

  return (
    <div className="grid grid-cols-[minmax(0,1fr)] gap-14 lg:grid-cols-2 lg:items-start lg:gap-10">
      <SponsorsCarousel>
        {sponsors.map((sponsor, index) => (
          <SponsorCard
            key={sponsor.nome}
            onOpen={() => setOpenIndex(index)}
            sponsor={sponsor}
          />
        ))}
      </SponsorsCarousel>

      <section aria-labelledby="lista-completa">
        <h2
          className="mb-6 text-center text-3xl font-bold uppercase lg:text-left lg:text-4xl"
          id="lista-completa"
        >
          Lista completa
        </h2>
        <ul className="mx-auto grid max-w-md grid-cols-3 gap-4 sm:gap-6 lg:max-w-none">
          {sponsors.map((sponsor, index) => (
            <li key={sponsor.nome}>
              <button
                aria-label={`Ver detalhes de ${sponsor.nome}`}
                className="group block w-full text-left focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring"
                onClick={() => setOpenIndex(index)}
                type="button"
              >
                <span className="flex aspect-square items-center justify-center bg-white p-4 shadow-[0_6px_0_hsl(var(--semana-contrast))] transition-transform group-hover:-translate-y-0.5">
                  <Image
                    alt=""
                    className="size-full object-contain"
                    height={sponsor.logo.height}
                    src={sponsor.logo.src}
                    width={sponsor.logo.width}
                  />
                </span>
                <span className="mt-3 block text-sm font-bold uppercase leading-tight">
                  {sponsor.nome}
                </span>
              </button>
            </li>
          ))}
        </ul>
      </section>

      <SponsorDialog index={openIndex} onIndexChange={setOpenIndex} sponsors={sponsors} />
    </div>
  )
}
