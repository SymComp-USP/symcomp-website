import type { Metadata } from 'next'

import { AboutPage } from '@/features/semana/components/about-page'

export const metadata: Metadata = {
  description:
    'A SymComp é um grupo de extensão do IME USP formado por alunos da graduação que dissemina a computação dentro e fora da universidade.',
}

export default function SobreNosPage() {
  return <AboutPage />
}
