import { Navigate, NavLink, Route, Routes } from 'react-router-dom'
import { useAuth } from './auth'
import Inventory from './pages/Inventory'
import Login from './pages/Login'
import Sets from './pages/Sets'

export default function App() {
  const { isLoggedIn } = useAuth()

  return (
    <div className="app">
      {isLoggedIn && <NavBar />}
      <main className="main">
        <Routes>
          <Route
            path="/login"
            element={isLoggedIn ? <Navigate to="/sets" replace /> : <Login />}
          />
          <Route
            path="/sets"
            element={
              <RequireAuth>
                <Sets />
              </RequireAuth>
            }
          />
          <Route
            path="/inventory"
            element={
              <RequireAuth>
                <Inventory />
              </RequireAuth>
            }
          />
          <Route path="*" element={<Navigate to={isLoggedIn ? '/sets' : '/login'} replace />} />
        </Routes>
      </main>
    </div>
  )
}

// Anything wrapped in this bounces to /login when there's no token — which
// also covers a session expiring mid-use, since the 401 handler clears it.
function RequireAuth({ children }) {
  const { isLoggedIn } = useAuth()
  return isLoggedIn ? children : <Navigate to="/login" replace />
}

function NavBar() {
  const { logout } = useAuth()

  return (
    <header className="nav">
      <span className="nav-brand">Prime Part Tracker</span>
      <nav className="nav-links">
        <NavLink to="/sets">Sets</NavLink>
        <NavLink to="/inventory">Inventory</NavLink>
      </nav>
      <button type="button" className="button button-quiet" onClick={logout}>
        Sign out
      </button>
    </header>
  )
}
