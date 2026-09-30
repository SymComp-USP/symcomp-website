'use client'

import { ChevronLeft, ChevronRight } from 'lucide-react'
import { Children, type KeyboardEvent, type ReactNode, useRef, useState } from 'react'

import { cn } from '@/lib/utils'

const arrowClassName =
  'flex size-10 shrink-0 items-center justify-center border-4 border-[hsl(var(--semana-contrast))] bg-white text-[hsl(var(--semana-contrast))] shadow-[0_4px_0_hsl(var(--semana-contrast))] transition-transform hover:-translate-y-0.5 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring active:translate-y-1 active:shadow-[0_2px_0_hsl(var(--semana-contrast))] disabled:pointer-events-none disabled:opacity-40 sm:size-12'

export function SponsorsCarousel({ children }: { children: ReactNode }) {
  const slides = Children.toArray(children)
  const trackRef = useRef<HTMLDivElement>(null)
  const [current, setCurrent] = useState(0)

  const handleScroll = () => {
    const track = trackRef.current
    if (!track) return
    setCurrent(Math.round(track.scrollLeft / track.clientWidth))
  }

  const goTo = (index: number) => {
    const track = trackRef.current
    if (!track) return
    const target = Math.max(0, Math.min(index, slides.length - 1))
    track.scrollTo({ left: target * track.clientWidth, behavior: 'smooth' })
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'ArrowLeft') {
      event.preventDefault()
      goTo(current - 1)
    } else if (event.key === 'ArrowRight') {
      event.preventDefault()
      goTo(current + 1)
    }
  }

  return (
    <div
      aria-label="Patrocinadores"
      aria-roledescription="carrossel"
      className="flex flex-col items-center gap-6"
      role="region"
    >
      {slides.length > 1 && (
        <div className="flex gap-2">
          {slides.map((_, index) => (
            <button
              aria-current={current === index ? 'true' : undefined}
              aria-label={`Ir para o patrocinador ${index + 1} de ${slides.length}`}
              className={cn(
                'size-4 border-2 border-[hsl(var(--semana-contrast))] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring',
                current === index ? 'bg-white' : 'bg-[hsl(var(--semana-sponsor-soft))]',
              )}
              key={index}
              onClick={() => goTo(index)}
              type="button"
            />
          ))}
        </div>
      )}

      <div className="flex w-full flex-wrap items-center justify-center gap-4 sm:flex-nowrap">
        {slides.length > 1 && (
          <button
            aria-label="Patrocinador anterior"
            className={arrowClassName}
            disabled={current === 0}
            onClick={() => goTo(current - 1)}
            type="button"
          >
            <ChevronLeft aria-hidden="true" />
          </button>
        )}

        <div
          className="order-first flex w-full min-w-0 snap-x sm:order-none sm:w-auto sm:flex-1 snap-mandatory overflow-x-auto py-4 [scrollbar-width:none] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring [&::-webkit-scrollbar]:hidden"
          onKeyDown={handleKeyDown}
          onScroll={handleScroll}
          ref={trackRef}
          tabIndex={0}
        >
          {slides.map((slide, index) => (
            <div
              aria-label={`${index + 1} de ${slides.length}`}
              aria-roledescription="slide"
              className="flex w-full shrink-0 snap-center justify-center px-3"
              key={index}
              role="group"
            >
              {slide}
            </div>
          ))}
        </div>

        {slides.length > 1 && (
          <button
            aria-label="Próximo patrocinador"
            className={arrowClassName}
            disabled={current === slides.length - 1}
            onClick={() => goTo(current + 1)}
            type="button"
          >
            <ChevronRight aria-hidden="true" />
          </button>
        )}
      </div>
    </div>
  )
}
