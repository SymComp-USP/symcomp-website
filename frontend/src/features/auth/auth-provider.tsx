'use client'

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'

import { login, logout, register, restoreSession, updateMyName } from './api'
import type { LoginInput, RegisterInput, User } from './types'

type AuthContextValue = {
  user: User | null
  loading: boolean
  login: (input: LoginInput) => Promise<User>
  register: (input: RegisterInput) => Promise<void>
  logout: () => Promise<void>
  updateName: (name: string) => Promise<User>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    restoreSession()
      .then(setUser)
      .finally(() => setLoading(false))
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      async login(input) {
        const user = await login(input)
        setUser(user)
        return user
      },
      async register(input) {
        await register(input)
      },
      async logout() {
        await logout()
        setUser(null)
      },
      async updateName(name) {
        const updated = await updateMyName(name)
        setUser(updated)
        return updated
      },
    }),
    [loading, user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const auth = useContext(AuthContext)
  if (!auth) throw new Error('useAuth must be used inside AuthProvider')
  return auth
}
