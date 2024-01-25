import { apiClient } from './client'

export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_verified: boolean
  created_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface SignupRequest {
  username: string
  email: string
  first_name: string
  last_name: string
  password: string
  password_confirm: string
}

export interface AuthResponse {
  user: User
  tokens: {
    access: string
    refresh: string
  }
}

export const authApi = {
  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await apiClient.post('/api/auth/login/', data)
    return response.data
  },

  signup: async (data: SignupRequest): Promise<AuthResponse> => {
    const response = await apiClient.post('/api/auth/register/', data)
    return response.data
  },

  logout: async (): Promise<void> => {
    const refreshToken = localStorage.getItem('refresh_token')
    if (refreshToken) {
      await apiClient.post('/api/auth/logout/', { refresh: refreshToken })
    }
  },

  getProfile: async (): Promise<User> => {
    const response = await apiClient.get('/api/auth/profile/')
    return response.data
  },

  updateProfile: async (data: Partial<User>): Promise<User> => {
    const response = await apiClient.patch('/api/auth/profile/', data)
    return response.data
  },

  changePassword: async (data: {
    old_password: string
    new_password: string
    new_password_confirm: string
  }): Promise<void> => {
    await apiClient.post('/api/auth/change-password/', data)
  },
}
