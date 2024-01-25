import { useState, useEffect, createContext, useContext, ReactNode } from 'react'
import { useQuery, useMutation, useQueryClient } from 'react-query'
import { authApi, User } from '../api/auth'
import toast from 'react-hot-toast'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  signup: (data: {
    username: string
    email: string
    first_name: string
    last_name: string
    password: string
    password_confirm: string
  }) => Promise<void>
  logout: () => void
  updateProfile: (data: Partial<User>) => Promise<void>
  changePassword: (data: {
    old_password: string
    new_password: string
    new_password_confirm: string
  }) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const queryClient = useQueryClient()

  // Check if user is logged in on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          const userData = await authApi.getProfile()
          setUser(userData)
        } catch (error) {
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
        }
      }
      setIsLoading(false)
    }

    checkAuth()
  }, [])

  const loginMutation = useMutation(authApi.login, {
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.tokens.access)
      localStorage.setItem('refresh_token', data.tokens.refresh)
      setUser(data.user)
      toast.success('Logged in successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Login failed')
    },
  })

  const signupMutation = useMutation(authApi.signup, {
    onSuccess: (data) => {
      localStorage.setItem('access_token', data.tokens.access)
      localStorage.setItem('refresh_token', data.tokens.refresh)
      setUser(data.user)
      toast.success('Account created successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Signup failed')
    },
  })

  const updateProfileMutation = useMutation(authApi.updateProfile, {
    onSuccess: (updatedUser) => {
      setUser(updatedUser)
      toast.success('Profile updated successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Profile update failed')
    },
  })

  const changePasswordMutation = useMutation(authApi.changePassword, {
    onSuccess: () => {
      toast.success('Password changed successfully!')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Password change failed')
    },
  })

  const login = async (email: string, password: string) => {
    try {
      await loginMutation.mutateAsync({ email, password })
    } catch (error) {
      // Error handling is done in the mutation
      throw error
    }
  }

  const signup = async (data: {
    username: string
    email: string
    first_name: string
    last_name: string
    password: string
    password_confirm: string
  }) => {
    await signupMutation.mutateAsync(data)
  }

  const logout = async () => {
    try {
      await authApi.logout()
    } catch (error) {
      // Ignore logout errors
    } finally {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setUser(null)
      queryClient.clear()
      toast.success('Logged out successfully!')
    }
  }

  const updateProfile = async (data: Partial<User>) => {
    await updateProfileMutation.mutateAsync(data)
  }

  const changePassword = async (data: {
    old_password: string
    new_password: string
    new_password_confirm: string
  }) => {
    await changePasswordMutation.mutateAsync(data)
  }

  const value: AuthContextType = {
    user,
    isLoading,
    login,
    signup,
    logout,
    updateProfile,
    changePassword,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
