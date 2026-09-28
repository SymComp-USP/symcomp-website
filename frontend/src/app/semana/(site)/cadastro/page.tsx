import { AuthCard } from '@/features/auth/components/auth-card'
import { RegisterForm } from '@/features/auth/components/register-form'

export default function RegisterPage() {
  return (
    <AuthCard
      description="Crie sua conta para participar das atividades da Semana."
      footer={{ text: 'Já tem uma conta?', label: 'Entrar', href: '/semana/login' }}
      title="Criar conta"
    >
      <RegisterForm />
    </AuthCard>
  )
}
