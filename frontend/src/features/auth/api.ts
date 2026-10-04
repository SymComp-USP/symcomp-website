import type { LoginInput, RegisterInput, User } from './types'

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? ''

let accessToken: string | undefined
let refreshPromise: Promise<void> | undefined

type ApiUser = {
  id: string
  name: string
  email: string
  is_admin: boolean
  is_verified: boolean
  created_at: string
}

type TokenResponse = { access_token: string }

function mapUser(user: ApiUser): User {
  return {
    id: user.id,
    name: user.name,
    email: user.email,
    isAdmin: user.is_admin,
    isVerified: user.is_verified,
    createdAt: user.created_at,
  }
}

export async function requestApi<T>(
  path: string,
  init: RequestInit = {},
  retry = true,
): Promise<T> {
  const headers = new Headers(init.headers)
  if (init.body && !(init.body instanceof FormData) && !headers.has('Content-Type'))
    headers.set('Content-Type', 'application/json')
  if (accessToken) headers.set('Authorization', `Bearer ${accessToken}`)

  const response = await fetch(`${API_URL}/api/v1${path}`, {
    ...init,
    headers,
    credentials: 'include',
  })

  if (response.status === 401 && retry && path !== '/auth/refresh') {
    try {
      await refresh()
      return requestApi<T>(path, init, false)
    } catch {
      accessToken = undefined
    }
  }

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null
    throw new Error(body?.detail ?? 'Não foi possível concluir a operação.')
  }

  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

async function refresh() {
  if (!refreshPromise) {
    refreshPromise = requestApi<TokenResponse>('/auth/refresh', { method: 'POST' }, false)
      .then((token) => {
        accessToken = token.access_token
      })
      .finally(() => {
        refreshPromise = undefined
      })
  }
  return refreshPromise
}

export async function login(input: LoginInput): Promise<User> {
  const body = new URLSearchParams({ username: input.email, password: input.password })
  const token = await requestApi<TokenResponse>('/auth/login', {
    method: 'POST',
    body,
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  accessToken = token.access_token
  return getCurrentUser()
}

export async function register(input: RegisterInput): Promise<void> {
  await requestApi('/user', { method: 'POST', body: JSON.stringify(input) })
}

export async function getCurrentUser(): Promise<User> {
  return mapUser(await requestApi<ApiUser>('/auth/me'))
}

export async function updateMyName(name: string): Promise<User> {
  return mapUser(
    await requestApi<ApiUser>('/user/me', {
      method: 'PATCH',
      body: JSON.stringify({ name }),
    }),
  )
}

export async function restoreSession(): Promise<User | null> {
  try {
    await refresh()
    return await getCurrentUser()
  } catch {
    accessToken = undefined
    return null
  }
}

export async function logout() {
  try {
    await requestApi<void>('/auth/logout', { method: 'POST' }, false)
  } finally {
    accessToken = undefined
  }
}
