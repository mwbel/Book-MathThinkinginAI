import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  avatar_url?: string
  is_active: boolean
  is_superuser: boolean
}

interface AuthState {
  user: User | null
  token: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

interface AuthActions {
  setUser: (user: User) => void
  setTokens: (token: string, refreshToken: string) => void
  login: (user: User, token: string, refreshToken: string) => void
  logout: () => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  clearError: () => void
}

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Actions
      setUser: (user: User) => {
        set({ user, isAuthenticated: true })
      },

      setTokens: (token: string, refreshToken: string) => {
        set({ token, refreshToken })
      },

      login: (user: User, token: string, refreshToken: string) => {
        set({
          user,
          token,
          refreshToken,
          isAuthenticated: true,
          error: null,
        })
      },

      logout: () => {
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
          error: null,
        })
      },

      setLoading: (isLoading: boolean) => {
        set({ isLoading })
      },

      setError: (error: string | null) => {
        set({ error })
      },

      clearError: () => {
        set({ error: null })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)