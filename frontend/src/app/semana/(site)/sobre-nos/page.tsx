import type { Metadata } from 'next'

import { AboutPage } from '@/features/semana/components/about-page'

export const metadata: Metadata = {
  title: 'Sobre nós | Semana da Computação',
  description:
    'Conheça a SymComp, grupo de extensão do IME USP que organiza a Semana da Computação e o ByteCafé.',
}

export default function SobreNosPage() {
  return <AboutPage />
}
