'use client'

import Image from 'next/image'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

import { semanaBody, semanaDisplay } from '@/features/semana/fonts'

const dots = [
  { left: '13%', top: '34%', size: 'size-[clamp(4px,0.55vw,8px)]', delay: '0ms' },
  { left: '20%', top: '38%', size: 'size-[clamp(6px,0.9vw,13px)]', delay: '850ms' },
  { left: '44%', top: '29%', size: 'size-[clamp(3px,0.4vw,6px)]', delay: '1500ms' },
  { left: '75%', top: '28%', size: 'size-[clamp(5px,0.75vw,11px)]', delay: '400ms' },
  { left: '82%', top: '41%', size: 'size-[clamp(6px,1vw,14px)]', delay: '1900ms' },
  { left: '89%', top: '52%', size: 'size-[clamp(3px,0.45vw,7px)]', delay: '1100ms' },
  { left: '17%', top: '52%', size: 'size-[clamp(7px,1.05vw,15px)]', delay: '600ms' },
  { left: '11%', top: '61%', size: 'size-[clamp(5px,0.8vw,12px)]', delay: '2200ms' },
  { left: '80%', top: '63%', size: 'size-[clamp(6px,0.9vw,13px)]', delay: '1300ms' },
  { left: '24%', top: '68%', size: 'size-[clamp(3px,0.45vw,7px)]', delay: '200ms' },
  { left: '38%', top: '25%', size: 'size-[clamp(4px,0.6vw,9px)]', delay: '1700ms' },
  { left: '67%', top: '69%', size: 'size-[clamp(4px,0.65vw,10px)]', delay: '900ms' },
  { left: '85%', top: '34%', size: 'size-[clamp(3px,0.4vw,6px)]', delay: '2100ms' },
  { left: '31%', top: '62%', size: 'size-[clamp(5px,0.85vw,12px)]', delay: '500ms' },
  { left: '72%', top: '56%', size: 'size-[clamp(3px,0.5vw,8px)]', delay: '1600ms' },
]

const loadingSegments = Array.from({ length: 18 }, (_, index) => index)

export default function Semana() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const previousBackgroundColor = document.body.style.backgroundColor
    document.body.style.backgroundColor = '#110f0f'

    return () => {
      document.body.style.backgroundColor = previousBackgroundColor
    }
  }, [])

  useEffect(() => {
    if (!isLoading) return

    const startedAt = Date.now()
    const duration = 1200
    const timer = window.setInterval(() => {
      const nextProgress = Math.min(100, ((Date.now() - startedAt) / duration) * 100)
      setProgress(nextProgress)

      if (nextProgress === 100) {
        window.clearInterval(timer)
        router.push('/semana/inicio')
      }
    }, 50)

    return () => window.clearInterval(timer)
  }, [isLoading, router])

  return (
    <main
      className={`${semanaBody.variable} ${semanaDisplay.variable} relative min-h-svh overflow-hidden bg-[#110f0f] px-4 text-white sm:px-8 xl:px-12`}
    >
      <div
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 overflow-hidden"
      >
        {dots.map((dot) => (
          <span
            className={`absolute -translate-x-1/2 -translate-y-1/2 bg-[#ffffff] opacity-80 animate-[pulse_4.2s_ease-in-out_infinite] ${dot.size}`}
            key={`${dot.left}-${dot.top}`}
            style={{ left: dot.left, top: dot.top, animationDelay: dot.delay }}
          />
        ))}
      </div>

      <article className="relative z-10 mx-auto flex min-h-svh w-full max-w-[1440px] flex-col items-center px-1 pb-6 pt-5 sm:pb-8 sm:pt-8 lg:px-8 lg:pt-10">
        <header
          aria-label="Marcas do evento"
          className="grid w-full grid-cols-3 items-start font-[family-name:var(--font-semana-display)] font-bold sm:items-center"
        >
          <Image
            alt="IME-USP"
            className="h-auto w-[clamp(44px,6.8vw,76px)]"
            height={52}
            priority
            src="/logo/ime_usp.svg"
            width={59}
          />
          <Image
            alt="SymComp"
            className="mx-auto h-auto w-[clamp(42px,5.7vw,72px)]"
            height={50}
            priority
            src="/logo/logo_symcomp_pixel.svg"
            width={50}
          />
          <p className="ml-auto w-fit border-2 border-[#efff22] px-2 py-1 text-right text-[clamp(12px,1.6vw,24px)] leading-[0.95] text-[#efff22] sm:px-3 sm:py-2">
            20
            <br />
            26
          </p>
        </header>

        <section className="mt-7 flex flex-col items-center text-center sm:mt-10 lg:mt-6">
          <h1 className="font-[family-name:var(--font-semana-display)] text-[clamp(24px,4vw,54px)] font-bold leading-none text-[#f5f7ee] [text-shadow:2px_3px_0_#050607]">
            SYMCOMP
          </h1>
          <p className="mt-2 font-[family-name:var(--font-semana-display)] text-[clamp(16px,1.8vw,25px)] font-bold uppercase leading-none text-[#f5f7ee]">
            Apresenta
          </p>
        </section>

        <section
          aria-label="Espaço para a marca da Semana da Computação"
          className="relative flex w-full flex-1 flex-col items-center justify-center py-7"
        >
          <Image
            alt="Logo colorida da Semana da Computação"
            className="h-auto w-[clamp(210px,27svh,420px)] max-w-[72vw]"
            height={223}
            priority
            src="/logo/logo_symcomp_colorida.svg"
            width={223}
          />
        </section>

        <div className="flex min-h-[clamp(96px,10vw,143px)] w-full items-center justify-center">
          {/* Previous CSS-drawn button retained for reference:
          <button
            className="relative flex min-h-[76px] w-fit items-center justify-center bg-white px-12 font-[family-name:var(--font-semana-display)] text-[clamp(19px,2.5vw,32px)] font-bold uppercase leading-none text-white"
            onClick={() => setIsLoading(true)}
            type="button"
          >
            <span className="absolute inset-[6px] bg-black" />
            <span className="relative z-10">Começar</span>
          </button>
          */}
          {isLoading ? (
            <div
              className={`flex w-full ${!isLoading ? 'animate-[pulse_500ms_ease-out_1]' : ''} flex-col items-center`}
            >
              <p
                aria-live="polite"
                className="mb-2 font-[family-name:var(--font-semana-display)] text-[clamp(10px,1.2vw,16px)] text-white"
              >
                CARREGANDO...
              </p>
              <div
                aria-label="Carregando"
                aria-valuemax={100}
                aria-valuemin={0}
                aria-valuenow={Math.round(progress)}
                className="h-[clamp(36px,5vw,56px)] w-[min(78vw,420px)] rounded-[5px] border-[4px] border-white bg-black p-[3px]"
                role="progressbar"
              >
                <div className="flex h-full w-full gap-[2px]">
                  {loadingSegments.map((segment) => (
                    <span
                      aria-hidden="true"
                      className={`flex-1 ${segment < (progress / 100) * loadingSegments.length ? 'bg-white' : 'bg-black'} ${segment < loadingSegments.length - 1 ? 'border-r border-white/80' : ''}`}
                      key={segment}
                    />
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <button
              aria-label="Começar"
              className="w-[min(72vw,420px)] animate-[pulse_4.2s_ease-in-out_infinite] transition-transform hover:scale-[1.02] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-white active:scale-[0.98]"
              onClick={() => setIsLoading(true)}
              type="button"
            >
              <Image
                alt="Começar"
                className="h-auto w-full"
                height={95}
                priority
                src="/semana/2026/comecar.svg"
                width={279}
              />
            </button>
          )}
        </div>

        <footer className="mt-auto flex w-full flex-col items-center pt-9 text-center sm:pt-12">
          <p className="font-[family-name:var(--font-semana-display)] text-[clamp(12px,1.3vw,18px)] font-bold uppercase leading-tight text-[#148180]">
            Um evento
            <br />
            patrocinado por:
          </p>
          <div
            aria-label="Marcas dos patrocinadores"
            className="mt-5 grid min-h-12 w-full grid-cols-3 items-center gap-3 sm:mt-7 sm:min-h-16"
          >
            <Image
              alt="Wild Life"
              className="h-auto w-[clamp(64px,8vw,120px)] justify-self-start"
              height={37}
              src="/logo/wild_life.svg"
              width={77}
            />
            <Image
              alt="Thomson Reuters"
              className="h-auto w-[clamp(110px,13vw,190px)] justify-self-center"
              height={57}
              src="/logo/rhomsom_reuters.svg"
              width={152}
            />
            <Image
              alt="nic.br"
              className="h-auto w-[clamp(78px,9vw,130px)] justify-self-end"
              height={50}
              src="/logo/nicbr.svg"
              width={92}
            />
          </div>
        </footer>
      </article>
    </main>
  )
}
