import { Barlow_Semi_Condensed, Silkscreen } from 'next/font/google'

export const semanaDisplay = Silkscreen({
  subsets: ['latin'],
  variable: '--font-semana-display',
  weight: ['400', '700'],
})

export const semanaBody = Barlow_Semi_Condensed({
  subsets: ['latin'],
  variable: '--font-semana-body',
  weight: ['400', '700'],
})
