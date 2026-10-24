// Holds the logged-in state for the whole app, so any screen can read it and
// the nav can react to logging in/out without prop-drilling.

import { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { api, clearToken, getToken, setToken } from './api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  // Seed from localStorage so a refresh doesn't log you out.
  const [token, setTokenState] = useState(() => getToken())

  const login = useCallback(async (credentials) => {
    const result = await api.login(credentials)
    setToken(result.access_token)
    setTokenState(result.access_token)
  }, [])

  const logout = useCallback(() => {
    clearToken()
    setTokenState(null)
  }, [])

  // Called when a request comes back 401 — the token was valid-looking but
  // the server rejected it (expired, or the account is gone).
  const sessionExpired = useCallback(() => {
    clearToken()
    setTokenState(null)
  }, [])

  const value = useMemo(
    () => ({ token, isLoggedIn: Boolean(token), login, logout, sessionExpired }),
    [token, login, logout, sessionExpired],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used inside <AuthProvider>')
  return context
}
