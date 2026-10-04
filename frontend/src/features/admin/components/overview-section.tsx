import { CircleAlert, Plus, Trophy, Users } from 'lucide-react'

import { Button } from '@/components/ui/button'

import type { AdminChallenge, AdminUser } from '../api'

type AdminTab = 'overview' | 'users' | 'challenges' | 'semanas' | 'activities' | 'points'

export function OverviewSection({
  users,
  challenges,
  onTab,
}: {
  users: AdminUser[]
  challenges: AdminChallenge[]
  onTab: (tab: AdminTab) => void
}) {
  return (
    <>
      <div className="grid gap-4 sm:grid-cols-3">
        <Metric label="Usuários ativos" value={users.length} icon={Users} />
        <Metric label="Desafios" value={challenges.length} icon={Trophy} />
        <Metric label="Módulos pendentes" value={2} icon={CircleAlert} />
      </div>
      <section className="mt-8 rounded-xl border border-slate-200 bg-white p-6">
        <h2 className="text-lg font-bold">Ações rápidas</h2>
        <div className="mt-4 flex flex-wrap gap-3">
          <Button onClick={() => onTab('users')}>
            <Plus size={16} /> Novo usuário
          </Button>
          <Button onClick={() => onTab('challenges')} variant="outline">
            <Plus size={16} /> Novo desafio
          </Button>
          <Button onClick={() => onTab('activities')} variant="outline">
            Ver atividades
          </Button>
        </div>
      </section>
    </>
  )
}

function Metric({
  label,
  value,
  icon: Icon,
}: {
  label: string
  value: number
  icon: typeof Users
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <Icon className="text-indigo-600" size={20} />
      <p className="mt-5 text-3xl font-black">{value}</p>
      <p className="text-sm text-slate-500">{label}</p>
    </div>
  )
}
