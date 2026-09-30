'use client'

import { Children, type KeyboardEvent, type ReactNode, useRef, useState } from 'react'

import { cn } from '@/lib/utils'

import { PixelChevron } from './pixel-chevron'

const arrowClassName =
  'relative z-10 flex size-9 shrink-0 -translate-y-8 items-center justify-center text-[hsl(var(--semana-contrast))] transition-transform hover:scale-110 focus-visible:outline-none focus-visible:ring-4 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-40 sm:size-12 lg:size-12'

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
      className="flex flex-col items-center gap-6 lg:-mt-2 lg:translate-x-8 xl:translate-x-16"
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

      <div className="relative mx-auto flex w-full max-w-md items-center gap-1 sm:gap-4 lg:max-w-[29.5rem] lg:gap-0">
        <div
          aria-hidden="true"
          className="pointer-events-none absolute left-1/2 top-[76%] h-2 lg:top-1/2 w-screen -translate-x-1/2 bg-[hsl(var(--semana-contrast))] lg:left-[calc(50%-14px-25cqw-2rem)] xl:left-[calc(50%-14px-25cqw-4rem)] lg:w-[calc(75cqw-190px)] lg:translate-x-0"
        />

        {slides.length > 1 && (
          <button
            aria-label="Patrocinador anterior"
            className={cn(arrowClassName, 'lg:-mr-6')}
            disabled={current === 0}
            onClick={() => goTo(current - 1)}
            type="button"
          >
            <PixelChevron className="h-8 w-auto sm:h-10 lg:h-10" direction="left" />
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
              className="flex w-full shrink-0 snap-center justify-center px-9"
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
            className={cn(arrowClassName, 'lg:-ml-6')}
            disabled={current === slides.length - 1}
            onClick={() => goTo(current + 1)}
            type="button"
          >
            <PixelChevron className="h-8 w-auto sm:h-10 lg:h-10" />
          </button>
        )}
      </div>
    </div>
  )
}
