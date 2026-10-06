import { AuthCard } from '@/features/auth/components/auth-card'
import { AuthNotice } from '@/features/auth/components/auth-notice'
import { LoginForm } from '@/features/auth/components/login-form'

const oauthErrors: Record<string, string> = {
  provider_unavailable: 'Este método de login ainda não está configurado.',
  invalid_provider: 'Provedor de autenticação inválido.',
  oauth_state: 'A tentativa de login expirou ou é inválida. Tente novamente.',
  oauth_denied: 'A autenticação foi cancelada.',
  oauth_invalid_profile: 'Não foi possível validar sua conta no provedor.',
  oauth_profile: 'O provedor não forneceu os dados necessários.',
  oauth_unverified_email: 'Confirme seu e-mail no provedor antes de continuar.',
  oauth_provider_error: 'O provedor não concluiu a autenticação. Tente novamente.',
  email_exists: 'Este e-mail já possui cadastro. Entre usando e-mail e senha.',
}

export default async function LoginPage({
  searchParams,
}: {
  searchParams: Promise<{ error?: string }>
}) {
  const { error } = await searchParams
  return (
    <AuthCard
      description="Acesse sua conta para acompanhar sua participação no evento."
      footer={{
        text: 'Ainda não tem conta?',
        label: 'Cadastre-se',
        href: '/semana/cadastro',
      }}
      title="Entrar"
    >
      {error && oauthErrors[error] && (
        <AuthNotice variant="error">{oauthErrors[error]}</AuthNotice>
      )}
      <LoginForm />
    </AuthCard>
  )
}
