import type { Metadata } from 'next'

import { SponsorsPage } from '@/features/semana/components/sponsors-page'

export const metadata: Metadata = {
  description:
    'Conheça as empresas patrocinadoras da 16ª Semana da Computação do IME USP.',
}

export default function PatrocinadoresPage() {
  return <SponsorsPage />
}
