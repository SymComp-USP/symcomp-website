export type User = {
  id: string
  name: string
  email: string
  isAdmin: boolean
  isVerified: boolean
  createdAt: string
}

export type LoginInput = {
  email: string
  password: string
}

export type RegisterInput = LoginInput & {
  name: string
}
