'use client'

import { useState } from 'react'

import { AuthCard } from '@/features/auth/components/auth-card'
import { AuthNotice } from '@/features/auth/components/auth-notice'
import { RegisterForm } from '@/features/auth/components/register-form'

export default function RegisterPage() {
  const [notice, setNotice] = useState<string>()

  return (
    <AuthCard
      description="Crie sua conta para participar das atividades da Semana."
      footer={{ text: 'Já tem uma conta?', label: 'Entrar', href: '/semana/login' }}
      notice={notice && <AuthNotice>{notice}</AuthNotice>}
      title="Criar conta"
    >
      <RegisterForm onSuccess={setNotice} />
    </AuthCard>
  )
}
