import Image from 'next/image'

import { cn } from '@/lib/utils'

import type { Sponsor } from '../sponsors'

// Sponsor icon inside the white pixel-art octagon from the design.
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
        'semana-pixel-octagon flex size-32 shrink-0 items-center justify-center bg-white',
        className,
      )}
    >
      <Image
        alt={sponsor.nome}
        className="size-[64%] object-contain"
        height={sponsor.logo.height}
        src={sponsor.logo.src}
        width={sponsor.logo.width}
      />
    </div>
  )
}
