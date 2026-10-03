'use client'

import { Menu } from 'lucide-react'
import Image from 'next/image'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import type { ReactNode } from 'react'

import { Button } from '@/components/ui/button'
import { AuthProvider, useAuth } from '@/features/auth/auth-provider'
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'
import { cn } from '@/lib/utils'

import { semanaBody, semanaDisplay } from '../fonts'
import { SemanaButton } from './semana-button'

const links = [
  { href: '/semana', label: 'Início' },
  { href: '/semana/cronograma', label: 'Programação' },
  { href: '/semana/presenca', label: 'Presença' },
  { href: '/semana/desafios', label: 'Desafios' },
  { href: '/semana/patrocinadores', label: 'Patrocinadores' },
  { href: '/semana/sobre-nos', label: 'Sobre nós' },
]

export function SemanaShell({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      <SemanaShellContent>{children}</SemanaShellContent>
    </AuthProvider>
  )
}

function SemanaShellContent({ children }: { children: ReactNode }) {
  const { user, loading, logout } = useAuth()
  const pathname = usePathname()
  const isSponsorsPage = pathname === '/semana/patrocinadores'
  const isSchedulePage = pathname === '/semana/cronograma'

  return (
    <div
      className={cn(
        'semana-theme grid min-h-svh grid-cols-[minmax(0,1fr)] grid-rows-[auto_1fr_auto] bg-background font-[family-name:var(--font-semana-body)] text-foreground',
        semanaBody.variable,
        semanaDisplay.variable,
      )}
    >
      <header
        className={cn(
          'sticky top-0 z-40 border-b-[6px] border-[hsl(var(--semana-contrast))] backdrop-blur',
          isSponsorsPage && 'bg-[hsl(var(--semana-sponsor))]',
          isSchedulePage && 'bg-[hsl(var(--semana-schedule))]',
          !isSponsorsPage && !isSchedulePage && 'bg-background/95',
        )}
      >
        <div className="mx-auto grid h-20 max-w-6xl grid-cols-3 items-center px-6">
          <Link className="flex items-center" href="/semana">
            <Image
              alt="IME-USP"
              className="h-auto w-12 brightness-0 invert sm:w-14"
              height={52}
              priority
              src="/logo/ime_usp.svg"
              width={59}
            />
          </Link>

          <div className="col-start-2 row-start-1 flex items-center justify-center">
            <Link href="/semana">
              <Image
                alt="Semana da Computação"
                height={47}
                priority
                src="/semana/2026/logo-horizontal.svg"
                width={196}
              />
            </Link>
          </div>

          <Sheet>
            <SheetTrigger asChild>
              <Button
                aria-label="Abrir menu"
                className="col-start-3 row-start-1 ml-auto"
                size="icon"
                variant="ghost"
              >
                <Menu aria-hidden="true" />
              </Button>
            </SheetTrigger>
            <SheetContent className="semana-theme border-l-[6px] border-[hsl(var(--semana-contrast))] bg-background font-[family-name:var(--font-semana-body)] text-foreground">
              <SheetHeader>
                <SheetTitle className="font-[family-name:var(--font-semana-display)] uppercase">
                  Semana da Computação
                </SheetTitle>
              </SheetHeader>
              <nav aria-label="Navegação principal" className="mt-8 flex flex-col gap-2">
                {links.map((link) => (
                  <SheetClose asChild key={link.href}>
                    <Button
                      asChild
                      className="justify-start font-[family-name:var(--font-semana-display)] uppercase"
                      variant="ghost"
                    >
                      <Link href={link.href}>{link.label}</Link>
                    </Button>
                  </SheetClose>
                ))}
                {user && (
                  <>
                    <SheetClose asChild>
                      <Button
                        asChild
                        className="justify-start font-[family-name:var(--font-semana-display)] uppercase"
                        variant="ghost"
                      >
                        <Link href="/semana/ranking">Ranking</Link>
                      </Button>
                    </SheetClose>
                    <SheetClose asChild>
                      <Button
                        asChild
                        className="justify-start font-[family-name:var(--font-semana-display)] uppercase"
                        variant="ghost"
                      >
                        <Link href="/semana/perfil">Perfil</Link>
                      </Button>
                    </SheetClose>
                  </>
                )}
                {!loading &&
                  (user ? (
                    <SheetClose asChild>
                      <Button
                        className="mt-2 justify-start"
                        onClick={logout}
                        variant="outline"
                      >
                        Sair
                      </Button>
                    </SheetClose>
                  ) : (
                    <SheetClose asChild>
                      <SemanaButton asChild className="mt-2">
                        <Link href="/semana/login">Entrar</Link>
                      </SemanaButton>
                    </SheetClose>
                  ))}
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </header>

      <div>{children}</div>

      <footer className="border-t-[6px] border-[hsl(var(--semana-contrast))] bg-[hsl(var(--semana-contrast))] text-white">
        <div className="mx-auto grid max-w-6xl gap-10 px-6 py-10 text-sm text-white/80 md:grid-cols-2">
          <section aria-labelledby="sponsors-title">
            <h2
              className="font-[family-name:var(--font-semana-display)] text-sm uppercase text-white"
              id="sponsors-title"
            >
              Patrocinado por
            </h2>
            <div className="mt-6 flex flex-wrap items-center gap-x-8 gap-y-6">
              <Image
                alt="Incognia"
                className="h-auto w-32 brightness-0 invert"
                height={158}
                src="/company-logos/incognia.webp"
                width={848}
              />
              <Image
                alt="Tako"
                className="h-auto w-28 brightness-0 invert"
                height={207}
                src="/company-logos/tako_logotipo.svg"
                width={791}
              />
              <Image
                alt="Asper"
                className="h-auto w-28 brightness-0 invert"
                height={592}
                src="/company-logos/colored-1.webp"
                width={2500}
              />
            </div>
          </section>

          <section aria-labelledby="supporters-title">
            <h2
              className="font-[family-name:var(--font-semana-display)] text-sm uppercase text-white"
              id="supporters-title"
            >
              Apoio
            </h2>
            <div className="mt-5 flex items-center gap-8">
              <Image alt="IME-USP" height={66} src="/logo/ime_branca.png" width={53} />
              <Image
                alt="Universidade de São Paulo"
                height={58}
                src="/logo/usp_branca.png"
                width={125}
              />
            </div>
          </section>
        </div>
      </footer>
    </div>
  )
}
