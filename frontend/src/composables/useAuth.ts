import { computed, ref } from 'vue'
import { ApiError } from '@/services/apiClient'
import { clearAccessToken, getAccessToken } from '@/services/authToken'
import { createAuthService } from '@/services/authService'
import type { AuthUser, LoginRequest, RegisterRequest } from '@/types/auth'

const authService = createAuthService()
const user = ref<AuthUser | null>(null)
const isInitialized = ref(false)
const isLoading = ref(false)
const isAuthenticated = computed(() => user.value !== null)
const initializationError = ref<string | null>(null)
let initialization: Promise<void> | null = null

export function useAuth() {
  async function initialize(): Promise<void> {
    if (isInitialized.value) return
    if (initialization) return initialization

    initialization = (async () => {
      isLoading.value = true
      try {
        if (getAccessToken()) {
          user.value = await authService.getCurrentUser()
        }
      } catch (error) {
        clearAccessToken()
        user.value = null
        if (!(error instanceof ApiError) || (error.status !== 401 && error.status !== 403)) {
          initializationError.value = 'We could not verify your session. Please sign in again.'
        }
      } finally {
        isLoading.value = false
        isInitialized.value = true
        initialization = null
      }
    })()

    return initialization
  }

  async function login(request: LoginRequest): Promise<void> {
    await authService.login(request)
    try {
      user.value = await authService.getCurrentUser()
      isInitialized.value = true
      initializationError.value = null
    } catch (error) {
      clearAccessToken()
      user.value = null
      throw error
    }
  }

  async function register(request: RegisterRequest): Promise<void> {
    await authService.register(request)
    await login({ email: request.email, password: request.password })
  }

  async function logout(): Promise<void> {
    try {
      await authService.logout()
    } finally {
      user.value = null
      isInitialized.value = true
    }
  }

  return {
    user,
    isInitialized,
    isLoading,
    isAuthenticated,
    initializationError,
    initialize,
    login,
    register,
    logout
  }
}
