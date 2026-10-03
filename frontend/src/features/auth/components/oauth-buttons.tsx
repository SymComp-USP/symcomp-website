'use client'

import { FaGithub, FaGoogle } from 'react-icons/fa'

export function OAuthButtons() {
  return (
    <div className="space-y-3">
      <a
        href="/api/v1/auth/oauth/google/login"
        className="flex w-full items-center justify-center gap-2 rounded-md border border-input bg-background px-4 py-2.5 text-sm font-medium transition-colors hover:bg-accent"
      >
        <FaGoogle aria-hidden="true" /> Continuar com Google
      </a>
      <a
        href="/api/v1/auth/oauth/github/login"
        className="flex w-full items-center justify-center gap-2 rounded-md border border-input bg-background px-4 py-2.5 text-sm font-medium transition-colors hover:bg-accent"
      >
        <FaGithub aria-hidden="true" /> Continuar com GitHub
      </a>
      <div
        className="flex items-center gap-3 text-xs text-muted-foreground"
        aria-hidden="true"
      >
        <span className="h-px flex-1 bg-border" />
        ou
        <span className="h-px flex-1 bg-border" />
      </div>
    </div>
  )
}
