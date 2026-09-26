import { CalendarDays, Menu, UserRound } from 'lucide-react'
import Image from 'next/image'
import Link from 'next/link'
import type { ReactNode } from 'react'

import { Button } from '@/components/ui/button'
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
  { href: '/semana/perfil', label: 'Perfil' },
]

export function SemanaShell({ children }: { children: ReactNode }) {
  return (
    <div
      className={cn(
        'semana-theme min-h-svh bg-background font-[family-name:var(--font-semana-body)] text-foreground',
        semanaBody.variable,
        semanaDisplay.variable,
      )}
    >
      <header className="sticky top-0 z-40 border-b-[6px] border-[hsl(var(--semana-contrast))] bg-background/95 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between px-6">
          <Link className="flex items-center gap-3" href="/semana/inicio">
            <Image
              alt="Semana da Computação"
              height={46}
              priority
              src="/semana/2025/logo-horizontal.svg"
              width={196}
            />
          </Link>

          <nav
            aria-label="Navegação principal"
            className="hidden items-center gap-1 md:flex"
          >
            {links.map((link) => (
              <Button asChild key={link.href} variant="ghost">
                <Link href={link.href}>{link.label}</Link>
              </Button>
            ))}
            <SemanaButton
              asChild
              className="ml-2 border-4 px-4 py-2 text-xs shadow-[0_4px_0_hsl(var(--semana-contrast))]"
            >
              <Link href="/semana/login">Entrar</Link>
            </SemanaButton>
          </nav>

          <Sheet>
            <SheetTrigger asChild>
              <Button
                aria-label="Abrir menu"
                className="md:hidden"
                size="icon"
                variant="ghost"
              >
                <Menu aria-hidden="true" />
              </Button>
            </SheetTrigger>
            <SheetContent className="semana-theme border-l-[6px] border-[hsl(var(--semana-contrast))] bg-background font-[family-name:var(--font-semana-body)] text-foreground">
              <SheetHeader>
                <SheetTitle>Semana da Computação</SheetTitle>
              </SheetHeader>
              <nav aria-label="Navegação móvel" className="mt-8 flex flex-col gap-2">
                {links.map((link) => (
                  <SheetClose asChild key={link.href}>
                    <Button asChild className="justify-start" variant="ghost">
                      <Link href={link.href}>{link.label}</Link>
                    </Button>
                  </SheetClose>
                ))}
                <SheetClose asChild>
                  <SemanaButton asChild className="mt-2">
                    <Link href="/semana/login">Entrar</Link>
                  </SemanaButton>
                </SheetClose>
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </header>

      {children}

      <footer className="border-t-[6px] border-[hsl(var(--semana-contrast))] bg-[hsl(var(--semana-contrast))] text-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-4 px-6 py-8 text-sm text-white/80 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <Image
              alt="IME-USP"
              height={38}
              src="/semana/2025/ime-usp-branca.svg"
              width={42}
            />
            <p>Semana da Computação — IME-USP</p>
          </div>
          <div className="flex gap-4">
            <Link
              className="inline-flex items-center gap-1 hover:text-foreground"
              href="/semana/cronograma"
            >
              <CalendarDays aria-hidden="true" size={16} /> Programação
            </Link>
            <Link
              className="inline-flex items-center gap-1 hover:text-foreground"
              href="/semana/perfil"
            >
              <UserRound aria-hidden="true" size={16} /> Perfil
            </Link>
          </div>
        </div>
      </footer>
    </div>
  )
}
