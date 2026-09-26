import type { LoginInput, RegisterInput, User } from './types'

export const mockUser: User = {
  id: '11111111-1111-4111-8111-111111111111',
  name: 'Ada Lovelace',
  email: 'ada@example.com',
  isAdmin: false,
  isVerified: true,
  createdAt: '2026-09-01T12:00:00-03:00',
}

export async function login(input: LoginInput): Promise<User> {
  void input
  return mockUser
}

export async function register(input: RegisterInput): Promise<User> {
  return { ...mockUser, name: input.name, email: input.email, isVerified: false }
}
