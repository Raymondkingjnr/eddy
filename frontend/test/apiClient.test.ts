import { afterEach, describe, expect, it, vi } from 'vitest'
import { ApiError, createApiClient } from '@/services/apiClient'

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('API client', () => {
  it('adds the bearer token and JSON headers to authenticated requests', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ id: 'user-id' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      })
    )
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient('/api', () => 'test-token')

    await expect(api<{ id: string }>('/users/me')).resolves.toEqual({ id: 'user-id' })

    const [url, options] = fetchMock.mock.calls[0] as [string, RequestInit]
    const headers = new Headers(options.headers)
    expect(url).toBe('/api/users/me')
    expect(headers.get('Authorization')).toBe('Bearer test-token')
    expect(headers.get('Accept')).toBe('application/json')
  })

  it('sends form-encoded login requests without attaching an existing token', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ access_token: 'new-token', token_type: 'bearer' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' }
      })
    )
    vi.stubGlobal('fetch', fetchMock)
    const api = createApiClient('/api', () => 'old-token')

    await api('/auth/jwt/login', {
      method: 'POST',
      body: new URLSearchParams({ username: 'learner@example.com', password: 'secret' }),
      auth: false
    })

    const [, options] = fetchMock.mock.calls[0] as [string, RequestInit]
    const headers = new Headers(options.headers)
    expect(headers.get('Content-Type')).toBe('application/x-www-form-urlencoded;charset=UTF-8')
    expect(headers.has('Authorization')).toBe(false)
    expect(options.body).toEqual(
      new URLSearchParams({ username: 'learner@example.com', password: 'secret' })
    )
  })

  it('surfaces FastAPI validation details with the HTTP status', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: [{ msg: 'Field required' }] }), {
          status: 422,
          headers: { 'Content-Type': 'application/json' }
        })
      )
    )
    const api = createApiClient('/api')

    await expect(api('/auth/register', { method: 'POST', body: {} })).rejects.toMatchObject({
      name: 'ApiError',
      status: 422,
      message: 'Field required'
    } satisfies Partial<ApiError>)
  })
})
