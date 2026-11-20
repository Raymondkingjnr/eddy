import { beforeEach, describe, expect, it } from 'vitest'
import { clearAccessToken, getAccessToken } from '@/services/authToken'
import { createAuthService } from '@/services/authService'
import type { ApiClient, ApiRequestOptions } from '@/services/apiClient'

function createFakeApi(response: unknown) {
  const calls: { path: string; options?: ApiRequestOptions }[] = []
  const api: ApiClient = async <T>(path: string, options?: ApiRequestOptions) => {
    calls.push({ path, options })
    return response as T
  }

  return { api, calls }
}

describe('auth service', () => {
  beforeEach(() => {
    clearAccessToken()
  })

  it('logs in with the OAuth2 form fields and stores the bearer token', async () => {
    const { api, calls } = createFakeApi({ access_token: 'test-token', token_type: 'bearer' })
    const service = createAuthService(api)

    await service.login({ email: 'learner@example.com', password: 'secret' })

    expect(calls[0]?.path).toBe('/auth/jwt/login')
    expect(calls[0]?.options?.method).toBe('POST')
    expect(calls[0]?.options?.auth).toBe(false)
    expect(calls[0]?.options?.body).toEqual(
      new URLSearchParams({ username: 'learner@example.com', password: 'secret' })
    )
    expect(getAccessToken()).toBe('test-token')
  })

  it('registers with the backend user schema', async () => {
    const user = {
      id: 'user-id',
      email: 'learner@example.com',
      fullname: 'Lesson Learner',
      is_active: true,
      is_verified: false
    }
    const { api, calls } = createFakeApi(user)
    const service = createAuthService(api)

    await expect(
      service.register({
        email: user.email,
        password: 'secret',
        fullname: user.fullname
      })
    ).resolves.toEqual(user)

    expect(calls[0]?.path).toBe('/auth/register')
    expect(calls[0]?.options?.body).toEqual({
      email: user.email,
      password: 'secret',
      fullname: user.fullname
    })
  })

  it('loads the signed-in user and clears the token after logout', async () => {
    const { api, calls } = createFakeApi(undefined)
    const service = createAuthService(api)
    clearAccessToken()

    await service.getCurrentUser()
    expect(calls[0]?.path).toBe('/users/me')

    await service.logout()
    expect(calls[1]?.path).toBe('/auth/jwt/logout')
    expect(calls[1]?.options?.method).toBe('POST')
    expect(getAccessToken()).toBeNull()
  })
})
