const storageKey = 'eddy:access-token'
let accessToken: string | null = null

export function getAccessToken(): string | null {
  if (accessToken) return accessToken
  if (typeof window === 'undefined') return null

  accessToken = window.sessionStorage.getItem(storageKey)
  return accessToken
}

export function setAccessToken(token: string): void {
  accessToken = token
  if (typeof window !== 'undefined') {
    window.sessionStorage.setItem(storageKey, token)
  }
}

export function clearAccessToken(): void {
  accessToken = null
  if (typeof window !== 'undefined') {
    window.sessionStorage.removeItem(storageKey)
  }
}
