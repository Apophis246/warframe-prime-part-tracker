// Thin wrapper around fetch: attaches the auth token, parses JSON, and turns
// API errors into thrown Errors so callers can just try/catch.
//
// Every path here is relative (/api/...). nginx proxies that prefix to the
// backend in production; Vite's dev server does the same locally. Nothing in
// the app needs to know the backend's address.

const TOKEN_KEY = 'ppt_token'

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY)
  } catch {
    return null
  }
}

export function setToken(token) {
  try {
    localStorage.setItem(TOKEN_KEY, token)
  } catch {
    /* private browsing, blocked storage — the session just won't persist */
  }
}

export function clearToken() {
  try {
    localStorage.removeItem(TOKEN_KEY)
  } catch {
    /* ignore */
  }
}

class ApiError extends Error {
  constructor(message, status) {
    super(message)
    this.status = status
  }
}

async function request(path, { method = 'GET', body, auth = true } = {}) {
  const headers = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  if (auth) {
    const token = getToken()
    if (token) headers.Authorization = `Bearer ${token}`
  }

  const response = await fetch(`/api${path}`, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  })

  if (response.status === 401) {
    clearToken()
    throw new ApiError('Your session has expired. Please log in again.', 401)
  }

  if (!response.ok) {
    throw new ApiError(await errorMessage(response), response.status)
  }

  if (response.status === 204) return null
  return response.json()
}

// FastAPI puts a string in `detail` for HTTPException, but an array of
// objects for validation failures. Flatten both into something displayable.
async function errorMessage(response) {
  let payload
  try {
    payload = await response.json()
  } catch {
    return `Request failed (${response.status})`
  }

  const detail = payload?.detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((d) => d.msg ?? JSON.stringify(d)).join('; ')
  }
  return `Request failed (${response.status})`
}

export const api = {
  register: (data) => request('/auth/register', { method: 'POST', body: data, auth: false }),
  login: (data) => request('/auth/login', { method: 'POST', body: data, auth: false }),
  items: () => request('/items'),
  inventory: () => request('/inventory'),
  setQuantity: (partRequirementId, quantityOwned) =>
    request(`/inventory/${partRequirementId}`, {
      method: 'PUT',
      body: { quantity_owned: quantityOwned },
    }),
  sets: () => request('/sets'),
}
