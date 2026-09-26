import { AuthCard } from '@/features/auth/components/auth-card'
import { LoginForm } from '@/features/auth/components/login-form'

export default function LoginPage() {
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
      <LoginForm />
    </AuthCard>
  )
}
