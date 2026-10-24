// Login and register share a screen — one toggle, two shapes of request.
// Registering does not log you in (the API returns a message, not a token),
// so on success we switch to the login form with the username prefilled.

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { useAuth } from '../auth'

export default function Login() {
  const [mode, setMode] = useState('login')
  const [identifier, setIdentifier] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [notice, setNotice] = useState(null)
  const [busy, setBusy] = useState(false)

  const { login } = useAuth()
  const navigate = useNavigate()

  const registering = mode === 'register'

  function switchMode(next) {
    setMode(next)
    setError(null)
    setNotice(null)
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError(null)
    setNotice(null)
    setBusy(true)

    try {
      if (registering) {
        await api.register({ username: identifier, email, password })
        setMode('login')
        setPassword('')
        setNotice('Account created. Log in to continue.')
      } else {
        // The API accepts either a username or an email. Decide which field
        // to send by whether what they typed looks like an address.
        const credentials = identifier.includes('@')
          ? { email: identifier, password }
          : { username: identifier, password }
        await login(credentials)
        navigate('/sets', { replace: true })
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-screen">
      <form className="card auth-card" onSubmit={handleSubmit}>
        <h1 className="auth-title">Prime Part Tracker</h1>
        <p className="auth-subtitle">
          {registering
            ? 'Create an account to start tracking your parts.'
            : 'Sign in to see which sets you can sell.'}
        </p>

        <label className="field">
          <span>{registering ? 'Username' : 'Username or email'}</span>
          <input
            value={identifier}
            onChange={(e) => setIdentifier(e.target.value)}
            autoComplete="username"
            required
          />
        </label>

        {registering && (
          <label className="field">
            <span>Email</span>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
            />
          </label>
        )}

        <label className="field">
          <span>Password</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete={registering ? 'new-password' : 'current-password'}
            required
          />
        </label>

        {error && <p className="message message-error">{error}</p>}
        {notice && <p className="message message-ok">{notice}</p>}

        <button className="button button-primary" type="submit" disabled={busy}>
          {busy ? 'Working…' : registering ? 'Create account' : 'Sign in'}
        </button>

        <p className="auth-switch">
          {registering ? 'Already have an account?' : "Don't have an account?"}{' '}
          <button
            type="button"
            className="link-button"
            onClick={() => switchMode(registering ? 'login' : 'register')}
          >
            {registering ? 'Sign in' : 'Create one'}
          </button>
        </p>
      </form>
    </div>
  )
}
