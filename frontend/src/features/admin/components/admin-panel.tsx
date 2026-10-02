'use client'

import { useEffect, useState } from 'react'
import {
  CalendarDays,
  CircleAlert,
  LayoutDashboard,
  LogOut,
  Shield,
  Trophy,
  Users,
} from 'lucide-react'
import { useRouter } from 'next/navigation'

import { useAuth } from '@/features/auth/auth-provider'

import {
  deleteAdminChallenge,
  deleteAdminUser,
  listAdminAtividades,
  listAdminChallenges,
  listAdminSemanas,
  listAdminUsers,
  updateAdminUser,
  type AdminAtividade,
  type AdminChallenge,
  type AdminSemana,
  type AdminUser,
} from '../api'

import { ActivitiesSection } from './activities-section'
import { ChallengesSection } from './challenges-section'
import { OverviewSection } from './overview-section'
import { PointsSection } from './points-section'
import { SemanasSection } from './semanas-section'
import { UsersSection } from './users-section'

type Tab = 'overview' | 'users' | 'challenges' | 'semanas' | 'activities' | 'points'

const tabs: { id: Tab; label: string; icon: typeof Users }[] = [
  { id: 'overview', label: 'Visão geral', icon: LayoutDashboard },
  { id: 'users', label: 'Usuários', icon: Users },
  { id: 'challenges', label: 'Desafios', icon: Trophy },
  { id: 'semanas', label: 'Semanas', icon: CalendarDays },
  { id: 'activities', label: 'Atividades', icon: CalendarDays },
  { id: 'points', label: 'Pontuação', icon: Shield },
]

export function AdminPanel() {
  const router = useRouter()
  const { user, loading, logout } = useAuth()
  const [tab, setTab] = useState<Tab>('overview')
  const [users, setUsers] = useState<AdminUser[]>([])
  const [challenges, setChallenges] = useState<AdminChallenge[]>([])
  const [semanas, setSemanas] = useState<AdminSemana[]>([])
  const [atividades, setAtividades] = useState<Record<number, AdminAtividade[]>>({})
  const [error, setError] = useState('')
  const [refresh, setRefresh] = useState(0)

  useEffect(() => {
    if (!loading && (!user || !user.isAdmin)) router.replace('/semana/login')
  }, [loading, router, user])

  useEffect(() => {
    if (!user?.isAdmin) return
    Promise.all([listAdminUsers(), listAdminChallenges(), listAdminSemanas()])
      .then(([userPage, challengePage, semanaList]) => {
        setUsers(userPage.items)
        setChallenges(challengePage.items)
        setSemanas(semanaList)
        return Promise.all(
          semanaList.map(
            async (semana) => [semana.id, await listAdminAtividades(semana.id)] as const,
          ),
        )
      })
      .then((activityLists) => {
        if (activityLists) setAtividades(Object.fromEntries(activityLists))
      })
      .catch((reason: Error) => setError(reason.message))
  }, [refresh, user])

  if (loading || !user?.isAdmin) return null

  async function removeUser(id: string) {
    if (!window.confirm('Remover este usuário?')) return
    try {
      await deleteAdminUser(id)
      setRefresh((value) => value + 1)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Não foi possível remover.')
    }
  }

  async function removeChallenge(id: string) {
    if (!window.confirm('Remover este desafio?')) return
    try {
      await deleteAdminChallenge(id)
      setRefresh((value) => value + 1)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Não foi possível remover.')
    }
  }

  async function toggleAdmin(adminUser: AdminUser) {
    try {
      await updateAdminUser(adminUser.id, { is_admin: !adminUser.is_admin })
      setRefresh((value) => value + 1)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Não foi possível atualizar.')
    }
  }

  return (
    <div className="min-h-svh bg-[#f7f5f0] text-slate-950">
      <aside className="fixed inset-y-0 left-0 hidden w-64 border-r border-slate-200 bg-white p-6 lg:block">
        <div className="flex items-center gap-2 text-lg font-black tracking-tight">
          <div className="rounded-lg bg-slate-950 p-2 text-white">
            <Shield size={18} />
          </div>{' '}
          SymComp Admin
        </div>
        <p className="mt-2 text-xs text-slate-500">Semana da Computação · 2026</p>
        <nav className="mt-10 space-y-1">
          {tabs.map(({ id, label, icon: Icon }) => (
            <button
              className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left text-sm font-medium ${tab === id ? 'bg-slate-950 text-white' : 'text-slate-600 hover:bg-slate-100'}`}
              key={id}
              onClick={() => setTab(id)}
            >
              <Icon size={17} />
              {label}
            </button>
          ))}
        </nav>
        <button
          className="absolute bottom-7 left-6 flex items-center gap-3 text-sm text-slate-500 hover:text-slate-950"
          onClick={logout}
        >
          <LogOut size={17} /> Sair
        </button>
      </aside>

      <main className="lg:ml-64">
        <header className="flex items-center justify-between border-b border-slate-200 bg-white px-5 py-5 sm:px-10">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.2em] text-indigo-600">
              Painel administrativo
            </p>
            <h1 className="mt-1 text-2xl font-black">
              {tabs.find((item) => item.id === tab)?.label}
            </h1>
          </div>
          <div className="text-right">
            <p className="text-sm font-semibold">{user.name}</p>
            <p className="text-xs text-slate-500">Administrador</p>
          </div>
        </header>
        <div className="border-b border-slate-200 bg-white px-5 py-3 lg:hidden">
          <div className="flex gap-2 overflow-auto">
            {tabs.map(({ id, label }) => (
              <button
                className={`whitespace-nowrap rounded-full px-3 py-1.5 text-xs font-bold ${tab === id ? 'bg-slate-950 text-white' : 'bg-slate-100'}`}
                key={id}
                onClick={() => setTab(id)}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
        <div className="mx-auto max-w-7xl p-5 sm:p-10">
          {error && (
            <div className="mb-6 flex items-center gap-2 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              <CircleAlert size={17} />
              {error}
            </div>
          )}
          {tab === 'overview' && (
            <OverviewSection users={users} challenges={challenges} onTab={setTab} />
          )}
          {tab === 'users' && (
            <UsersSection
              users={users}
              currentUserId={user.id}
              onCreated={() => setRefresh((value) => value + 1)}
              onDelete={removeUser}
              onToggleAdmin={toggleAdmin}
            />
          )}
          {tab === 'challenges' && (
            <ChallengesSection
              challenges={challenges}
              semanas={semanas}
              onSaved={(savedChallenge) => {
                setChallenges((current) => {
                  const exists = current.some((item) => item.id === savedChallenge.id)
                  return exists
                    ? current.map((item) =>
                        item.id === savedChallenge.id ? savedChallenge : item,
                      )
                    : [savedChallenge, ...current]
                })
              }}
              onDelete={removeChallenge}
            />
          )}
          {tab === 'semanas' && (
            <SemanasSection
              atividades={atividades}
              semanas={semanas}
              onActivityChanged={() => setRefresh((value) => value + 1)}
              onChanged={() => setRefresh((value) => value + 1)}
            />
          )}
          {tab === 'activities' && (
            <ActivitiesSection
              atividades={atividades}
              semanas={semanas}
              onActivityChanged={() => setRefresh((value) => value + 1)}
            />
          )}
          {tab === 'points' && <PointsSection challenges={challenges} />}
        </div>
      </main>
    </div>
  )
}
