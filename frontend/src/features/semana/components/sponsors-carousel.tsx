'use client'

import { ChevronLeft, ChevronRight } from 'lucide-react'
import { Children, type KeyboardEvent, type ReactNode, useRef, useState } from 'react'

import { cn } from '@/lib/utils'

const arrowClassName =
  'relative z-10 flex size-11 shrink-0 items-center justify-center text-[hsl(var(--semana-contrast))] transition-transform hover:scale-110 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-40'

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
        <div className="flex gap-2 lg:order-last">
          {slides.map((_, index) => (
            <button
              aria-current={current === index ? 'true' : undefined}
              aria-label={`Ir para o patrocinador ${index + 1} de ${slides.length}`}
              className={cn(
                'size-3 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring',
                current === index ? 'bg-white' : 'bg-[hsl(var(--semana-contrast))]',
              )}
              key={index}
              onClick={() => goTo(index)}
              type="button"
            />
          ))}
        </div>
      )}

      <div className="relative mx-auto flex w-full max-w-md items-center gap-1 sm:gap-4">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute left-1/2 top-[62%] h-2 w-screen -translate-x-1/2 bg-[hsl(var(--semana-contrast))] lg:left-auto lg:right-0 lg:translate-x-0"
        />

        {slides.length > 1 && (
          <button
            aria-label="Patrocinador anterior"
            className={arrowClassName}
            disabled={current === 0}
            onClick={() => goTo(current - 1)}
            type="button"
          >
            <ChevronLeft aria-hidden="true" className="size-9" strokeWidth={4} />
          </button>
        )}

        <div
          className="relative flex min-w-0 flex-1 snap-x snap-mandatory overflow-x-auto py-4 [scrollbar-width:none] focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring [&::-webkit-scrollbar]:hidden"
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
            <ChevronRight aria-hidden="true" className="size-9" strokeWidth={4} />
          </button>
        )}
      </div>
    </div>
  )
}
