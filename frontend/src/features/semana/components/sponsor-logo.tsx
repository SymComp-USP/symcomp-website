import Image from 'next/image'

import { cn } from '@/lib/utils'

import type { Sponsor } from '../sponsors'

// The logos come in different colors, so they are rendered white on the
// sponsor tone, like in the shell footer.
export function SponsorLogo({
  sponsor,
  className,
}: {
  sponsor: Sponsor
  className?: string
}) {
  return (
    <div
      className={cn(
        'flex h-32 w-full items-center justify-center border-4 border-[hsl(var(--semana-contrast))] bg-[hsl(var(--semana-sponsor-soft))] px-6 py-8',
        className,
      )}
    >
      <Image
        alt={sponsor.nome}
        className="h-full w-auto max-w-full object-contain brightness-0 invert"
        height={sponsor.logo.height}
        src={sponsor.logo.src}
        width={sponsor.logo.width}
      />
    </div>
  )
}
