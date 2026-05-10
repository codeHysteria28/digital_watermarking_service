import { createContext, useContext, useEffect, useState } from 'react'
import { api, type UserProfile } from '@/lib/api'

interface AuthContextValue {
  isAuthenticated: boolean
  token: string | null
  user: UserProfile | null
  login: (email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

const TOKEN_KEY = 'auth_token'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState<UserProfile | null>(null)

  // Fetch profile whenever we have a token
  useEffect(() => {
    if (!token) { setUser(null); return }
    api.getProfile(token)
      .then(setUser)
      .catch(() => {
        // Token is invalid or expired — clear it
        localStorage.removeItem(TOKEN_KEY)
        setToken(null)
      })
  }, [token])

  const login = async (email: string, password: string) => {
    const { access_token } = await api.login(email, password)
    localStorage.setItem(TOKEN_KEY, access_token)
    setToken(access_token)
  }

  const logout = () => {
    localStorage.removeItem(TOKEN_KEY)
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated: !!token, token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
