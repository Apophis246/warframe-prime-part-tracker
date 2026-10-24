// The payoff screen. /sets does the comparing server-side, so this is mostly
// presentation: group by status, put complete sets first since those are the
// ones you can actually sell, and show exactly what's missing on partial ones.
//
// It also fetches /items and /inventory. /sets alone can't drive the "sold a
// set" action because PartStatusOut carries no part_requirement_id, and part
// names aren't unique within an item (Akbronco Prime lists "Bronco Prime"
// twice). /items gives the ids, /inventory gives the current counts, and both
// are keyed by id — so the subtraction is unambiguous.

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
  const [partsByItem, setPartsByItem] = useState({})  // item id -> part requirements
  const [owned, setOwned] = useState({})              // part id -> quantity owned
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [query, setQuery] = useState('')
  const [showEmpty, setShowEmpty] = useState(false)
  const [sellingId, setSellingId] = useState(null)

  const { sessionExpired } = useAuth()

  const handleError = useCallback(
    (err) => {
      if (err.status === 401) sessionExpired()
      else setError(err.message)
    },
    [sessionExpired],
  )

  const load = useCallback(async () => {
    const [setData, itemData, inventoryData] = await Promise.all([
      api.sets(),
      api.items(),
      api.inventory(),
    ])
    setSets(setData)
    setPartsByItem(Object.fromEntries(itemData.map((i) => [i.id, i.part_requirements])))
    setOwned(
      Object.fromEntries(inventoryData.map((e) => [e.part_requirement_id, e.quantity_owned])),
    )
  }, [])

  useEffect(() => {
    let cancelled = false
    load()
      .catch((err) => {
        if (!cancelled) handleError(err)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [load, handleError])

  // Subtract one set's worth of parts: each part drops by exactly what the set
  // requires, so spares survive. Floors at zero defensively, though a complete
  // set means every part already meets its requirement.
  const sellSet = useCallback(
    async (itemId) => {
      const parts = partsByItem[itemId]
      if (!parts) return

      setSellingId(itemId)
      setError(null)
      try {
        await Promise.all(
          parts.map((part) => {
            const remaining = Math.max(0, (owned[part.id] ?? 0) - part.quantity_required)
            return api.setQuantity(part.id, remaining)
          }),
        )
        await load()
      } catch (err) {
        handleError(err)
      } finally {
        setSellingId(null)
      }
    },
    [partsByItem, owned, load, handleError],
  )

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
                  <SetCard
                    key={set.id}
                    set={set}
                    parts={partsByItem[set.id]}
                    owned={owned}
                    onSell={sellSet}
                    busy={sellingId === set.id}
                  />
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

function SetCard({ set, parts, owned, onSell, busy }) {
  const [confirming, setConfirming] = useState(false)
  const missing = set.part_status.filter((p) => p.quantity_owned < p.quantity_required)

  // How many parts survive the sale — shown so it's obvious when you have
  // spares and the set will still be sellable afterwards.
  const leftovers = (parts ?? []).reduce(
    (total, part) => total + Math.max(0, (owned[part.id] ?? 0) - part.quantity_required),
    0,
  )

  // A stray click shouldn't silently delete parts, but a modal for something
  // you'll do often is heavy. The button asks once, in place.
  useEffect(() => {
    if (!confirming) return
    const timer = setTimeout(() => setConfirming(false), 4000)
    return () => clearTimeout(timer)
  }, [confirming])

  function handleClick() {
    if (confirming) {
      setConfirming(false)
      onSell(set.id)
    } else {
      setConfirming(true)
    }
  }

  return (
    <article className={`card set-card set-${set.status}`}>
      <header className="set-card-header">
        <h3>{set.name}</h3>
        <span className={`badge badge-${set.status}`}>{set.status}</span>
      </header>

      {set.status === 'complete' ? (
        <>
          <p className="set-note">
            All parts owned.
            {leftovers > 0 && ` ${leftovers} spare part${leftovers === 1 ? '' : 's'} beyond this set.`}
          </p>
          <button
            type="button"
            className={`button button-sell ${confirming ? 'is-confirming' : ''}`}
            onClick={handleClick}
            disabled={busy || !parts}
          >
            {busy ? 'Removing…' : confirming ? 'Confirm — remove parts' : 'Sold a set'}
          </button>
        </>
      ) : (
        <ul className="missing-list">
          {missing.map((part, index) => (
            <li key={`${part.part_name}-${index}`}>
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
