import { Link as LinkIcon, X } from 'lucide-react'

import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogTitle,
} from '@/components/ui/dialog'
import { cn } from '@/lib/utils'

import { semanaBody, semanaDisplay } from '../fonts'
import type { Sponsor } from '../sponsors'
import { PixelChevron } from './pixel-chevron'
import { SponsorLogo } from './sponsor-logo'

const navButtonClassName =
  'flex size-10 shrink-0 items-center justify-center text-[hsl(var(--semana-sponsor-soft))] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-30'

function SponsorDetails({ sponsor }: { sponsor: Sponsor }) {
  return (
    <>
      <div className="flex items-center gap-4 px-6 pb-6 pt-16">
        <SponsorLogo className="size-24 lg:size-28" sponsor={sponsor} />
        <div className="min-w-0 space-y-2">
          <DialogTitle className="text-xl font-bold uppercase leading-tight lg:text-2xl">
            {sponsor.nome}
          </DialogTitle>
          {sponsor.site && (
            <a
              className="inline-flex items-center gap-2 bg-[hsl(var(--semana-sponsor-soft))] px-3 py-1 text-sm font-bold uppercase text-white hover:underline focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring"
              href={sponsor.site}
              rel="noopener noreferrer"
              target="_blank"
            >
              Site
              <LinkIcon aria-hidden="true" className="size-4" />
              <span className="sr-only"> (abre em nova aba)</span>
            </a>
          )}
        </div>
      </div>

      {sponsor.sobre ? (
        <section className="flex flex-1 flex-col">
          <h3 className="border-t-[3px] border-white bg-[hsl(var(--semana-sponsor-soft))] py-2.5 text-center text-base font-bold uppercase text-white">
            Sobre a empresa
          </h3>
          <DialogDescription className="flex-1 border-t-[3px] border-white p-5 text-base text-white/90 lg:p-7 lg:text-lg">
            {sponsor.sobre}
          </DialogDescription>
        </section>
      ) : (
        <DialogDescription className="sr-only">
          Patrocinador da Semana da Computação.
        </DialogDescription>
      )}
    </>
  )
}

export function SponsorDialog({
  sponsors,
  index,
  onIndexChange,
}: {
  sponsors: Sponsor[]
  index: number | null
  onIndexChange: (index: number | null) => void
}) {
  const sponsor = index === null ? undefined : sponsors[index]

  return (
    <Dialog
      onOpenChange={(open) => {
        if (!open) onIndexChange(null)
      }}
      open={sponsor !== undefined}
    >
      <DialogContent
        className={cn(
          'semana-theme flex w-[calc(100%-1rem)] max-w-xl flex-col lg:max-w-[38rem] items-center gap-4 border-0 bg-transparent p-0 font-[family-name:var(--font-semana-body)] text-white shadow-none sm:rounded-none [&>button:last-child]:hidden',
          semanaBody.variable,
          semanaDisplay.variable,
        )}
      >
        {sponsor && index !== null && (
          <>
            <div className="flex w-full items-center gap-1">
              <button
                aria-label="Patrocinador anterior"
                className={navButtonClassName}
                disabled={index === 0}
                onClick={() => onIndexChange(index - 1)}
                type="button"
              >
                <PixelChevron className="h-8 w-auto" direction="left" />
              </button>

              <div className="semana-notch min-w-0 flex-1 bg-white p-[3px] [--notch:20px]">
                <div className="semana-notch relative flex max-h-[80svh] flex-col overflow-y-auto bg-black [--notch:20px] lg:min-h-[37.5rem]">
                  <DialogClose className="absolute right-7 top-7 z-10 flex size-8 items-center justify-center text-white focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring">
                    <X aria-hidden="true" />
                    <span className="sr-only">Fechar</span>
                  </DialogClose>
                  <SponsorDetails key={index} sponsor={sponsor} />
                </div>
              </div>

              <button
                aria-label="Próximo patrocinador"
                className={navButtonClassName}
                disabled={index === sponsors.length - 1}
                onClick={() => onIndexChange(index + 1)}
                type="button"
              >
                <PixelChevron className="h-8 w-auto" />
              </button>
            </div>

            {sponsors.length > 1 && (
              <div className="flex gap-2">
                {sponsors.map((item, dotIndex) => (
                  <button
                    aria-current={dotIndex === index ? 'true' : undefined}
                    aria-label={`Ir para o patrocinador ${dotIndex + 1} de ${sponsors.length}`}
                    className={cn(
                      'size-3 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring',
                      dotIndex === index
                        ? 'bg-[hsl(var(--semana-sponsor-soft))]'
                        : 'bg-white',
                    )}
                    key={item.nome}
                    onClick={() => onIndexChange(dotIndex)}
                    type="button"
                  />
                ))}
              </div>
            )}
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
