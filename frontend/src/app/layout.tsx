import './styles/globals.css'

import { Inter, Silkscreen } from 'next/font/google'

export const inter = Inter({ subsets: ['latin'] })

export const silkscreen = Silkscreen({
  subsets: ['latin'],
  weight: '400',
  variable: '--font-silkscreen',
  display: 'swap',
})

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-background text-foreground`}>
        {children}
      </body>
    </html>
  )
}
