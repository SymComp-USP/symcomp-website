import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Política de Privacidade | Semana da Computação',
  description: 'Política de privacidade da Semana da Computação.',
}

export default function PrivacyPage() {
  return (
    <main className="mx-auto w-full max-w-4xl px-6 py-12 sm:py-16">
      <article className="space-y-6 rounded-none border-[6px] border-[hsl(var(--semana-contrast))] bg-card p-6 text-card-foreground sm:p-10">
        <header className="space-y-3">
          <h1 className="font-[family-name:var(--font-semana-display)] text-4xl uppercase sm:text-5xl">
            Política de privacidade
          </h1>
          <p className="text-muted-foreground">
            Consulte abaixo nossa política de privacidade e controles de cookies.
          </p>
        </header>
        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">Dados usados no acesso à conta</h2>
          <p>
            A SymComp trata nome, endereço de e-mail e o identificador da conta para
            criar, autenticar e manter seu perfil na Semana da Computação.
          </p>
        </section>
        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">Login com Google e GitHub</h2>
          <p>
            No Google, solicitamos somente <code>openid</code>, <code>email</code> e{' '}
            <code>profile</code>. No GitHub, solicitamos <code>read:user</code> e{' '}
            <code>user:email</code>. Esses dados confirmam seu e-mail e identificam sua
            conta.
          </p>
          <p>
            Tokens de acesso fornecidos por Google e GitHub são usados somente durante a
            autenticação e não são armazenados pela aplicação.
          </p>
        </section>
        <section className="space-y-3">
          <h2 className="text-2xl font-semibold">Política completa</h2>
          <iframe
            className="h-[70rem] w-full border-0"
            src="https://www.iubenda.com/privacy-policy/40876019"
            title="Política de Privacidade"
          />
          <p className="text-sm text-muted-foreground">
            Se a política não aparecer, abra{' '}
            <a
              className="underline underline-offset-4"
              href="https://www.iubenda.com/privacy-policy/40876019"
            >
              Política de Privacidade
            </a>
            .
          </p>
        </section>
        <div>
          <a
            className="rounded-full border-2 border-[hsl(var(--semana-contrast))] px-4 py-2 font-medium text-[hsl(var(--semana-contrast))]"
            href="https://www.iubenda.com/privacy-policy/40876019/cookie-policy"
            title="Política de Cookies"
          >
            Política de Cookies
          </a>
        </div>
      </article>
    </main>
  )
}
