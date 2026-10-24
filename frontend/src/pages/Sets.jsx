// The payoff screen. /sets does all the comparing server-side, so this is
// mostly presentation: group by status, put complete sets first since those
// are the ones you can actually sell, and show exactly what's missing on the
// partial ones.

import { useCallback, useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import { useAuth } from '../auth'

const GROUPS = [
  { status: 'complete', title: 'Complete sets', blurb: 'Ready to sell as a full set.' },
  { status: 'partial', title: 'Partial sets', blurb: 'Some parts owned — sell individually, or finish the set.' },
  { status: 'none', title: 'Not started', blurb: 'No parts owned yet.' },
]

export default function Sets() {
  const [sets, setSets] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('')
  const [showEmpty, setShowEmpty] = useState(false)

  const { sessionExpired } = useAuth()

  const handleError = useCallback(
    (err) => {
      if (err.status === 401) sessionExpired()
      else setError(err.message)
    },
    [sessionExpired],
  )

  useEffect(() => {
    let cancelled = false
    api
      .sets()
      .then((data) => {
        if (!cancelled) setSets(data)
      })
      .catch((err) => {
        if (!cancelled) handleError(err)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [handleError])

  const counts = useMemo(() => {
    const tally = { complete: 0, partial: 0, none: 0 }
    sets.forEach((set) => {
      tally[set.status] += 1
    })
    return tally
  }, [sets])

  const grouped = useMemo(() => {
    const needle = query.trim().toLowerCase()
    const matching = needle
      ? sets.filter((set) => set.name.toLowerCase().includes(needle))
      : sets
    return GROUPS.map((group) => ({
      ...group,
      sets: matching.filter((set) => set.status === group.status),
    }))
  }, [sets, query])

  if (loading) return <p className="state">Working out what you can sell…</p>

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Sets</h1>
          <p className="page-subtitle">What you can sell right now, and what's close.</p>
        </div>
      </header>

      <div className="summary">
        <SummaryTile label="Complete" value={counts.complete} tone="complete" />
        <SummaryTile label="Partial" value={counts.partial} tone="partial" />
        <SummaryTile label="Not started" value={counts.none} tone="none" />
      </div>

      <div className="toolbar">
        <input
          className="search"
          type="search"
          placeholder="Search sets…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <label className="checkbox">
          <input
            type="checkbox"
            checked={showEmpty}
            onChange={(e) => setShowEmpty(e.target.checked)}
          />
          <span>Show not-started</span>
        </label>
      </div>

      {error && <p className="message message-error">{error}</p>}

      {grouped
        .filter((group) => group.status !== 'none' || showEmpty)
        .map((group) => (
          <section key={group.status} className="group">
            <div className="group-header">
              <h2>
                {group.title} <span className="group-count">{group.sets.length}</span>
              </h2>
              <p className="group-blurb">{group.blurb}</p>
            </div>

            {group.sets.length === 0 ? (
              <p className="state state-quiet">Nothing here yet.</p>
            ) : (
              <div className="set-grid">
                {group.sets.map((set) => (
                  <SetCard key={set.id} set={set} />
                ))}
              </div>
            )}
          </section>
        ))}
    </div>
  )
}

function SummaryTile({ label, value, tone }) {
  return (
    <div className={`card tile tile-${tone}`}>
      <span className="tile-value">{value}</span>
      <span className="tile-label">{label}</span>
    </div>
  )
}

function SetCard({ set }) {
  const missing = set.part_status.filter((p) => p.quantity_owned < p.quantity_required)

  return (
    <article className={`card set-card set-${set.status}`}>
      <header className="set-card-header">
        <h3>{set.name}</h3>
        <span className={`badge badge-${set.status}`}>{set.status}</span>
      </header>

      {set.status === 'complete' ? (
        <p className="set-note">All parts owned.</p>
      ) : (
        <ul className="missing-list">
          {missing.map((part) => (
            <li key={part.part_name + part.quantity_required}>
              <span className="missing-name">{part.part_name}</span>
              <span className="missing-count">
                {part.quantity_owned} / {part.quantity_required}
              </span>
            </li>
          ))}
        </ul>
      )}
    </article>
  )
}
