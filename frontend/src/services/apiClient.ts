import { getAccessToken } from '@/services/authToken'

export interface ApiRequestOptions extends Omit<RequestInit, 'body'> {
  body?: BodyInit | object | null
  auth?: boolean
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
    readonly detail?: unknown
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export type ApiClient = <T>(path: string, options?: ApiRequestOptions) => Promise<T>

const defaultBaseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, '') || '/api'

function isBodyInit(body: BodyInit | object): body is BodyInit {
  return (
    typeof body === 'string' ||
    body instanceof Blob ||
    body instanceof FormData ||
    body instanceof URLSearchParams ||
    body instanceof ArrayBuffer ||
    (typeof ReadableStream !== 'undefined' && body instanceof ReadableStream)
  )
}

function getErrorMessage(payload: unknown, status: number): string {
  if (payload && typeof payload === 'object' && 'detail' in payload) {
    const detail = payload.detail
    if (typeof detail === 'string') return detail
    if (Array.isArray(detail)) {
      const messages = detail
        .map((item: unknown) =>
          item && typeof item === 'object' && 'msg' in item && typeof item.msg === 'string'
            ? item.msg
            : null
        )
        .filter((message): message is string => message !== null)
      if (messages.length > 0) return messages.join('. ')
    }
  }

  return `Request failed with status ${status}.`
}

export function createApiClient(
  baseUrl = defaultBaseUrl,
  tokenProvider: () => string | null = getAccessToken
): ApiClient {
  return async <T>(path: string, options: ApiRequestOptions = {}): Promise<T> => {
    const { auth = true, body, headers: requestHeaders, ...requestOptions } = options
    const headers = new Headers(requestHeaders)
    headers.set('Accept', 'application/json')

    if (auth) {
      const token = tokenProvider()
      if (token) headers.set('Authorization', `Bearer ${token}`)
    }

    let requestBody: BodyInit | undefined
    if (body !== undefined) {
      if (body === null) {
        requestBody = 'null'
        if (!headers.has('Content-Type')) headers.set('Content-Type', 'application/json')
      } else if (body instanceof URLSearchParams) {
        requestBody = body
        if (!headers.has('Content-Type')) {
          headers.set('Content-Type', 'application/x-www-form-urlencoded;charset=UTF-8')
        }
      } else if (isBodyInit(body)) {
        requestBody = body
      } else {
        requestBody = JSON.stringify(body)
        if (!headers.has('Content-Type')) headers.set('Content-Type', 'application/json')
      }
    }

    const response = await fetch(`${baseUrl}${path.startsWith('/') ? path : `/${path}`}`, {
      ...requestOptions,
      headers,
      body: requestBody
    })

    if (response.status === 204) return undefined as T

    const responseText = await response.text()
    let payload: unknown
    if (responseText) {
      try {
        payload = JSON.parse(responseText)
      } catch {
        payload = { detail: responseText }
      }
    }

    if (!response.ok) {
      throw new ApiError(getErrorMessage(payload, response.status), response.status, payload)
    }

    return payload as T
  }
}

export const apiClient = createApiClient()
