import { clearAccessToken, setAccessToken } from '@/services/authToken'
import { apiClient, type ApiClient } from '@/services/apiClient'
import type { AccessTokenResponse, AuthUser, LoginRequest, RegisterRequest } from '@/types/auth'

export function createAuthService(api: ApiClient = apiClient) {
  return {
    async login(request: LoginRequest): Promise<void> {
      const form = new URLSearchParams({
        username: request.email,
        password: request.password,
      })
      const response = await api<AccessTokenResponse>('/auth/jwt/login', {
        method: 'POST',
        body: form,
        auth: false,
      })

      if (
        !response.access_token ||
        typeof response.token_type !== 'string' ||
        response.token_type.toLowerCase() !== 'bearer'
      ) {
        throw new Error('The authentication server returned an invalid access token.')
      }

      setAccessToken(response.access_token)
    },

    async register(request: RegisterRequest): Promise<AuthUser> {
      return api<AuthUser>('/auth/register', {
        method: 'POST',
        body: request,
        auth: false,
      })
    },

    async getCurrentUser(): Promise<AuthUser> {
      return api<AuthUser>('/users/me')
    },

    async logout(): Promise<void> {
      try {
        await api<void>('/auth/jwt/logout', { method: 'POST' })
      } finally {
        clearAccessToken()
      }
    },
  }
}
