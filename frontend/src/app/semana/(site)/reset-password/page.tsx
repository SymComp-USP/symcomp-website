import { AuthCard } from '@/features/auth/components/auth-card'
import { PasswordResetForm } from '@/features/auth/components/password-reset-form'

export default async function PasswordResetPage({
  searchParams,
}: {
  searchParams: Promise<{ token?: string }>
}) {
  const { token } = await searchParams

  return (
    <AuthCard
      description={
        token
          ? 'Escolha uma nova senha para sua conta.'
          : 'Informe seu e-mail para receber um link de redefinição.'
      }
      footer={{ text: 'Lembrou sua senha?', label: 'Entrar', href: '/semana/login' }}
      title="Recuperar senha"
    >
      <PasswordResetForm token={token} />
    </AuthCard>
  )
}
