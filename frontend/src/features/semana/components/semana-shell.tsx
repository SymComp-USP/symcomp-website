'use client'

import { Menu } from 'lucide-react'
import Image from 'next/image'
import Link from 'next/link'
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
  { href: '/semana/inicio', label: 'Início' },
  { href: '/semana/cronograma', label: 'Programação' },
  { href: '/semana/ranking', label: 'Ranking' },
  { href: '/semana/perfil', label: 'Perfil' },
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

  return (
    <div
      className={cn(
        'semana-theme min-h-svh bg-background font-[family-name:var(--font-semana-body)] text-foreground',
        semanaBody.variable,
        semanaDisplay.variable,
      )}
    >
      <header className="sticky top-0 z-40 border-b-[6px] border-[hsl(var(--semana-contrast))] bg-background/95 backdrop-blur">
        <div className="mx-auto grid h-20 max-w-6xl grid-cols-3 items-center px-6">
          <Link className="flex items-center" href="/semana/inicio">
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
            <Link href="/semana/inicio">
              <Image
                alt="Semana da Computação"
                height={47}
                priority
                src="/semana/2026/logo-horizontal.svg"
                width={196}
              />
            </Link>
          </div>

          <nav
            aria-label="Navegação principal"
            className="col-start-3 row-start-1 hidden items-center justify-end gap-1 md:flex"
          >
            {links.map((link) => (
              <Button
                asChild
                className="font-[family-name:var(--font-semana-display)] text-xs uppercase"
                key={link.href}
                variant="ghost"
              >
                <Link href={link.href}>{link.label}</Link>
              </Button>
            ))}
            {!loading &&
              (user ? (
                <Button className="ml-2" onClick={logout} variant="outline">
                  Sair
                </Button>
              ) : (
                <SemanaButton
                  asChild
                  className="ml-2 border-4 px-4 py-2 text-xs shadow-[0_4px_0_hsl(var(--semana-contrast))]"
                >
                  <Link href="/semana/login">Entrar</Link>
                </SemanaButton>
              ))}
          </nav>

          <Sheet>
            <SheetTrigger asChild>
              <Button
                aria-label="Abrir menu"
                className="col-start-3 row-start-1 ml-auto md:hidden"
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
              <nav aria-label="Navegação móvel" className="mt-8 flex flex-col gap-2">
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

      {children}

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
