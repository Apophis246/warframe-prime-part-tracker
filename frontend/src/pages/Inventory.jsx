// The screen you actually live in: every prime item, every part, with the
// quantity you own. Edits save themselves — typing updates the UI instantly
// and a PUT follows shortly after, so you can run down a list without
// stopping to click Save on each row.

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { api } from '../api'
import { useAuth } from '../auth'

const SAVE_DELAY_MS = 500

export default function Inventory() {
  const [items, setItems] = useState([])
  const [owned, setOwned] = useState({})      // part_requirement_id -> quantity
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(0)     // count of in-flight saves
  const [query, setQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')

  const { sessionExpired } = useAuth()
  const timers = useRef({})

  const handleError = useCallback(
    (err) => {
      if (err.status === 401) sessionExpired()
      else setError(err.message)
    },
    [sessionExpired],
  )

  useEffect(() => {
    let cancelled = false

    async function load() {
      try {
        const [catalog, inventory] = await Promise.all([api.items(), api.inventory()])
        if (cancelled) return
        setItems(catalog)
        setOwned(
          Object.fromEntries(inventory.map((e) => [e.part_requirement_id, e.quantity_owned])),
        )
      } catch (err) {
        if (!cancelled) handleError(err)
      } finally {
        if (!cancelled) setLoading(false)
      }
    }

    load()
    return () => {
      cancelled = true
    }
  }, [handleError])

  // Clear any pending saves if the screen goes away mid-edit.
  useEffect(() => {
    const pending = timers.current
    return () => Object.values(pending).forEach(clearTimeout)
  }, [])

  const changeQuantity = useCallback(
    (partId, rawValue) => {
      const quantity = Math.max(0, Number.isFinite(rawValue) ? Math.floor(rawValue) : 0)

      // Update the UI immediately; the request catches up.
      setOwned((prev) => ({ ...prev, [partId]: quantity }))

      clearTimeout(timers.current[partId])
      timers.current[partId] = setTimeout(async () => {
        delete timers.current[partId]
        setSaving((n) => n + 1)
        try {
          await api.setQuantity(partId, quantity)
        } catch (err) {
          handleError(err)
        } finally {
          setSaving((n) => n - 1)
        }
      }, SAVE_DELAY_MS)
    },
    [handleError],
  )

  const visible = useMemo(() => {
    const needle = query.trim().toLowerCase()
    return items.filter((item) => {
      if (typeFilter !== 'all' && item.item_type !== typeFilter) return false
      if (!needle) return true
      return item.name.toLowerCase().includes(needle)
    })
  }, [items, query, typeFilter])

  if (loading) return <p className="state">Loading your inventory…</p>

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>Inventory</h1>
          <p className="page-subtitle">
            Set how many of each part you have. Changes save on their own.
          </p>
        </div>
        <span className={`save-indicator ${saving > 0 ? 'is-saving' : ''}`}>
          {saving > 0 ? 'Saving…' : 'All changes saved'}
        </span>
      </header>

      <div className="toolbar">
        <input
          className="search"
          type="search"
          placeholder="Search items…"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <div className="segmented">
          {[
            ['all', 'All'],
            ['warframe', 'Warframes'],
            ['weapon', 'Weapons'],
          ].map(([value, label]) => (
            <button
              key={value}
              type="button"
              className={typeFilter === value ? 'is-active' : ''}
              onClick={() => setTypeFilter(value)}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      {error && <p className="message message-error">{error}</p>}

      <p className="result-count">
        {visible.length} of {items.length} items
      </p>

      <div className="item-grid">
        {visible.map((item) => (
          <ItemCard
            key={item.id}
            item={item}
            owned={owned}
            onChange={changeQuantity}
          />
        ))}
      </div>

      {visible.length === 0 && <p className="state">No items match that search.</p>}
    </div>
  )
}

function ItemCard({ item, owned, onChange }) {
  const complete = item.part_requirements.every(
    (part) => (owned[part.id] ?? 0) >= part.quantity_required,
  )

  return (
    <article className={`card item-card ${complete ? 'is-complete' : ''}`}>
      <header className="item-card-header">
        <h2>{item.name}</h2>
        <span className={`tag tag-${item.item_type}`}>{item.item_type}</span>
      </header>

      <ul className="part-list">
        {item.part_requirements.map((part) => {
          const have = owned[part.id] ?? 0
          const met = have >= part.quantity_required
          return (
            <li key={part.id} className={`part-row ${met ? 'is-met' : ''}`}>
              <span className="part-name">{part.part_name}</span>
              <span className="part-required">need {part.quantity_required}</span>
              <div className="stepper">
                <button
                  type="button"
                  aria-label={`Decrease ${part.part_name}`}
                  onClick={() => onChange(part.id, have - 1)}
                  disabled={have === 0}
                >
                  −
                </button>
                <input
                  type="number"
                  min="0"
                  value={have}
                  onChange={(e) => onChange(part.id, Number(e.target.value))}
                  aria-label={`${item.name} ${part.part_name} owned`}
                />
                <button
                  type="button"
                  aria-label={`Increase ${part.part_name}`}
                  onClick={() => onChange(part.id, have + 1)}
                >
                  +
                </button>
              </div>
            </li>
          )
        })}
      </ul>
    </article>
  )
}
