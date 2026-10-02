'use client'

import { useState } from 'react'
import { Check, Plus, Shield, Trash2 } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'

import { createAdminUser, type AdminUser } from '../api'

export function UsersSection({
  users,
  currentUserId,
  onCreated,
  onDelete,
  onToggleAdmin,
}: {
  users: AdminUser[]
  currentUserId: string
  onCreated: () => void
  onDelete: (id: string) => void
  onToggleAdmin: (user: AdminUser) => void
}) {
  const [open, setOpen] = useState(false)
  return (
    <section>
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500">Contas, permissões e verificação</p>
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
                      className="text-slate-400 hover:text-indigo-600 disabled:cursor-not-allowed disabled:opacity-40"
                      disabled={item.id === currentUserId}
                      onClick={() => onToggleAdmin(item)}
                      title={
                        item.id === currentUserId
                          ? 'Você não pode alterar seu próprio acesso de administrador'
                          : undefined
                      }
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
