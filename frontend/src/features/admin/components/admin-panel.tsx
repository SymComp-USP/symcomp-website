'use client'

import { useEffect, useState } from 'react'
import {
  CalendarDays,
  Check,
  CircleAlert,
  LayoutDashboard,
  LogOut,
  Plus,
  Shield,
  Trash2,
  Trophy,
  Users,
} from 'lucide-react'
import { useRouter } from 'next/navigation'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAuth } from '@/features/auth/auth-provider'

import {
  createAdminChallenge,
  createAdminSemana,
  createAdminUser,
  deleteAdminChallenge,
  deleteAdminSemana,
  deleteAdminUser,
  listAdminChallenges,
  listAdminSemanas,
  listAdminUsers,
  uploadAdminChallengeImage,
  updateAdminSemana,
  updateAdminUser,
  type AdminChallenge,
  type AdminSemana,
  type AdminUser,
} from '../api'

type Tab = 'overview' | 'users' | 'challenges' | 'activities' | 'points'

const tabs: { id: Tab; label: string; icon: typeof Users }[] = [
  { id: 'overview', label: 'Visão geral', icon: LayoutDashboard },
  { id: 'users', label: 'Usuários', icon: Users },
  { id: 'challenges', label: 'Desafios', icon: Trophy },
  { id: 'activities', label: 'Semanas', icon: CalendarDays },
  { id: 'points', label: 'Pontuação', icon: Shield },
]

export function AdminPanel() {
  const router = useRouter()
  const { user, loading, logout } = useAuth()
  const [tab, setTab] = useState<Tab>('overview')
  const [users, setUsers] = useState<AdminUser[]>([])
  const [challenges, setChallenges] = useState<AdminChallenge[]>([])
  const [semanas, setSemanas] = useState<AdminSemana[]>([])
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

  async function toggleAdmin(user: AdminUser) {
    try {
      await updateAdminUser(user.id, { is_admin: !user.is_admin })
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
            <Overview users={users} challenges={challenges} onTab={setTab} />
          )}
          {tab === 'users' && (
            <UsersSection
              users={users}
              onCreated={() => setRefresh((value) => value + 1)}
              onDelete={removeUser}
              onToggleAdmin={toggleAdmin}
            />
          )}
          {tab === 'challenges' && (
            <ChallengesSection
              challenges={challenges}
              semanas={semanas}
              onCreated={() => setRefresh((value) => value + 1)}
              onDelete={removeChallenge}
            />
          )}
          {tab === 'activities' && (
            <SemanasSection
              semanas={semanas}
              onChanged={() => setRefresh((value) => value + 1)}
            />
          )}
          {tab === 'points' && (
            <Unavailable
              title="Pontuação manual"
              text="O backend já possui o endpoint de ajuste por participante, mas falta uma consulta administrativa de participantes por usuário para tornar este fluxo seguro no painel."
            />
          )}
        </div>
      </main>
    </div>
  )
}

function Overview({
  users,
  challenges,
  onTab,
}: {
  users: AdminUser[]
  challenges: AdminChallenge[]
  onTab: (tab: Tab) => void
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

function UsersSection({
  users,
  onCreated,
  onDelete,
  onToggleAdmin,
}: {
  users: AdminUser[]
  onCreated: () => void
  onDelete: (id: string) => void
  onToggleAdmin: (user: AdminUser) => void
}) {
  const [open, setOpen] = useState(false)
  return (
    <section>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-slate-500">Contas, permissões e verificação</p>
        </div>
        <Button onClick={() => setOpen(true)}>
          <Plus size={16} /> Novo usuário
        </Button>
      </div>
      {open && (
        <UserForm
          onDone={() => {
            setOpen(false)
            onCreated()
          }}
        />
      )}
      <div className="mt-5 overflow-hidden rounded-xl border border-slate-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase text-slate-500">
            <tr>
              <th className="p-4">Nome</th>
              <th className="p-4">E-mail</th>
              <th className="p-4">Status</th>
              <th className="p-4" />
            </tr>
          </thead>
          <tbody>
            {users.map((item) => (
              <tr className="border-b border-slate-100 last:border-0" key={item.id}>
                <td className="p-4 font-semibold">{item.name}</td>
                <td className="p-4 text-slate-500">{item.email}</td>
                <td className="p-4">
                  {item.is_admin ? 'Admin' : 'Usuário'} ·{' '}
                  {item.is_verified ? 'verificado' : 'pendente'}
                </td>
                <td className="p-4 text-right">
                  <div className="flex justify-end gap-3">
                    <button
                      aria-label={`Alternar admin de ${item.name}`}
                      className="text-slate-400 hover:text-indigo-600"
                      onClick={() => onToggleAdmin(item)}
                    >
                      <Shield size={17} />
                    </button>
                    <button
                      aria-label={`Remover ${item.name}`}
                      className="text-slate-400 hover:text-red-600"
                      onClick={() => onDelete(item.id)}
                    >
                      <Trash2 size={17} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

function UserForm({ onDone }: { onDone: () => void }) {
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    is_admin: false,
    is_verified: true,
  })
  const [error, setError] = useState('')
  async function submit(event: React.FormEvent) {
    event.preventDefault()
    try {
      await createAdminUser(form)
      onDone()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Não foi possível criar.')
    }
  }
  return (
    <form
      className="my-5 grid gap-3 rounded-xl border border-indigo-100 bg-indigo-50 p-5 sm:grid-cols-2"
      onSubmit={submit}
    >
      <Input
        required
        placeholder="Nome"
        value={form.name}
        onChange={(event) => setForm({ ...form, name: event.target.value })}
      />
      <Input
        required
        placeholder="E-mail"
        type="email"
        value={form.email}
        onChange={(event) => setForm({ ...form, email: event.target.value })}
      />
      <Input
        required
        minLength={8}
        placeholder="Senha"
        type="password"
        value={form.password}
        onChange={(event) => setForm({ ...form, password: event.target.value })}
      />
      <label className="flex items-center gap-2 text-sm">
        <input
          checked={form.is_admin}
          type="checkbox"
          onChange={(event) => setForm({ ...form, is_admin: event.target.checked })}
        />{' '}
        Administrador
      </label>
      {error && <p className="text-sm text-red-700">{error}</p>}
      <Button className="sm:col-span-2" type="submit">
        <Check size={16} /> Criar usuário
      </Button>
    </form>
  )
}

function ChallengesSection({
  challenges,
  semanas,
  onCreated,
  onDelete,
}: {
  challenges: AdminChallenge[]
  semanas: AdminSemana[]
  onCreated: () => void
  onDelete: (id: string) => void
}) {
  const [open, setOpen] = useState(false)
  return (
    <section>
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">Desafios e recompensas da Semana</p>
        <Button onClick={() => setOpen(true)}>
          <Plus size={16} /> Novo desafio
        </Button>
      </div>
      {open && (
        <ChallengeForm
          semanas={semanas}
          onDone={() => {
            setOpen(false)
            onCreated()
          }}
        />
      )}
      <div className="mt-5 grid gap-4 md:grid-cols-2">
        {challenges.map((item) => (
          <article
            className="rounded-xl border border-slate-200 bg-white p-5"
            key={item.id}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-indigo-600">
                  {item.scoring_type}
                </p>
                <h2 className="mt-1 font-bold">{item.title}</h2>
              </div>
              <button
                aria-label={`Remover ${item.title}`}
                className="text-slate-400 hover:text-red-600"
                onClick={() => onDelete(item.id)}
              >
                <Trash2 size={17} />
              </button>
            </div>
            <p className="mt-4 text-sm text-slate-500">
              {item.points_value} pontos · encerra em{' '}
              {new Date(item.finishes_at).toLocaleDateString('pt-BR')}
            </p>
          </article>
        ))}
      </div>
    </section>
  )
}

function ChallengeForm({
  onDone,
  semanas,
}: {
  onDone: () => void
  semanas: AdminSemana[]
}) {
  const latestSemanaId = semanas
    .slice()
    .sort((a, b) => b.ano - a.ano || b.id - a.id)[0]
    ?.id.toString()
  const [form, setForm] = useState({
    title: '',
    prompt: '',
    scoring_type: 'input' as const,
    finishes_at: '',
    points_value: 10,
    input_answer: '',
    semana_id: latestSemanaId ?? '',
  })
  const [image, setImage] = useState<File | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!latestSemanaId) return
    setForm((current) => ({
      ...current,
      semana_id: current.semana_id || latestSemanaId,
    }))
  }, [latestSemanaId])

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    try {
      const challenge = await createAdminChallenge({
        ...form,
        semana_id: form.semana_id ? Number(form.semana_id) : undefined,
        finishes_at: new Date(form.finishes_at).toISOString(),
      })
      if (image) await uploadAdminChallengeImage(challenge.id, image)
      onDone()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Não foi possível criar.')
    }
  }
  return (
    <form
      className="my-5 grid gap-3 rounded-xl border border-indigo-100 bg-indigo-50 p-5 sm:grid-cols-2"
      onSubmit={submit}
    >
      <Input
        required
        placeholder="Título"
        value={form.title}
        onChange={(event) => setForm({ ...form, title: event.target.value })}
      />
      <div className="flex h-10 items-center rounded-md border border-input bg-background px-3 text-sm text-slate-500">
        Resposta
      </div>
      <select
        className="h-10 rounded-md border border-input bg-background px-3 text-sm"
        value={form.semana_id}
        onChange={(event) => setForm({ ...form, semana_id: event.target.value })}
      >
        <option value="">Sem associar a uma Semana</option>
        {semanas.map((semana) => (
          <option key={semana.id} value={semana.id}>
            {semana.nome} ({semana.ano})
          </option>
        ))}
      </select>
      <Input
        className="sm:col-span-2"
        placeholder="Descrição"
        value={form.prompt}
        onChange={(event) => setForm({ ...form, prompt: event.target.value })}
      />
      <Input
        required
        className="sm:col-span-2"
        placeholder="Resposta esperada"
        value={form.input_answer}
        onChange={(event) => setForm({ ...form, input_answer: event.target.value })}
      />
      <label className="sm:col-span-2">
        <span className="mb-2 block text-sm font-medium">Imagem do desafio</span>
        <Input
          accept="image/*"
          type="file"
          onChange={(event) => setImage(event.target.files?.[0] ?? null)}
        />
      </label>
      <Input
        required
        type="datetime-local"
        value={form.finishes_at}
        onChange={(event) => setForm({ ...form, finishes_at: event.target.value })}
      />
      <Input
        required
        min={0}
        type="number"
        value={form.points_value}
        onChange={(event) =>
          setForm({ ...form, points_value: Number(event.target.value) })
        }
      />
      {error && <p className="text-sm text-red-700">{error}</p>}
      <Button className="sm:col-span-2" type="submit">
        <Check size={16} /> Criar desafio
      </Button>
    </form>
  )
}

function SemanasSection({
  semanas,
  onChanged,
}: {
  semanas: AdminSemana[]
  onChanged: () => void
}) {
  const [form, setForm] = useState({ nome: '', ano: new Date().getFullYear() })
  const [error, setError] = useState('')

  async function create(event: React.FormEvent) {
    event.preventDefault()
    try {
      await createAdminSemana(form)
      setForm({ nome: '', ano: new Date().getFullYear() })
      onChanged()
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : 'Não foi possível criar a Semana.',
      )
    }
  }

  async function rename(semana: AdminSemana) {
    const nome = window.prompt('Nome da Semana', semana.nome)
    if (!nome || nome === semana.nome) return
    try {
      await updateAdminSemana(semana.id, { nome })
      onChanged()
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : 'Não foi possível atualizar a Semana.',
      )
    }
  }

  async function remove(semana: AdminSemana) {
    if (semana.challenge_count || semana.participant_count) {
      setError('Uma Semana com desafios ou participantes não pode ser removida.')
      return
    }
    if (!window.confirm(`Remover ${semana.nome}?`)) return
    try {
      await deleteAdminSemana(semana.id)
      onChanged()
    } catch (reason) {
      setError(
        reason instanceof Error ? reason.message : 'Não foi possível remover a Semana.',
      )
    }
  }

  return (
    <section>
      <p className="text-sm text-slate-500">
        Uma Semana pode conter vários desafios; os desafios podem ser associados pelo seu
        `semana_id`.
      </p>
      <form
        className="mt-5 grid gap-3 rounded-xl border border-indigo-100 bg-indigo-50 p-5 sm:grid-cols-[1fr_140px_auto]"
        onSubmit={create}
      >
        <Input
          required
          placeholder="Nome da Semana"
          value={form.nome}
          onChange={(event) => setForm({ ...form, nome: event.target.value })}
        />
        <Input
          required
          type="number"
          value={form.ano}
          onChange={(event) => setForm({ ...form, ano: Number(event.target.value) })}
        />
        <Button type="submit">
          <Plus size={16} /> Criar Semana
        </Button>
      </form>
      {error && <p className="mt-3 text-sm text-red-700">{error}</p>}
      <div className="mt-5 grid gap-4 md:grid-cols-2">
        {semanas.map((semana) => (
          <article
            className="rounded-xl border border-slate-200 bg-white p-5"
            key={semana.id}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-bold uppercase tracking-wider text-indigo-600">
                  {semana.ano}
                </p>
                <h2 className="mt-1 font-bold">{semana.nome}</h2>
              </div>
              <div className="flex gap-3">
                <button
                  className="text-sm font-semibold text-indigo-600"
                  onClick={() => rename(semana)}
                >
                  Editar
                </button>
                <button
                  aria-label={`Remover ${semana.nome}`}
                  className="text-slate-400 hover:text-red-600"
                  onClick={() => remove(semana)}
                >
                  <Trash2 size={17} />
                </button>
              </div>
            </div>
            <p className="mt-4 text-sm text-slate-500">
              {semana.challenge_count} desafios · {semana.participant_count} participantes
            </p>
          </article>
        ))}
      </div>
    </section>
  )
}

function Unavailable({ title, text }: { title: string; text: string }) {
  return (
    <section className="max-w-2xl rounded-xl border border-amber-200 bg-amber-50 p-6">
      <CircleAlert className="text-amber-700" size={24} />
      <h2 className="mt-4 text-xl font-bold">{title}</h2>
      <p className="mt-2 text-sm leading-6 text-amber-900">{text}</p>
    </section>
  )
}
