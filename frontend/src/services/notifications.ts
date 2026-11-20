import { toast } from 'vue-sonner'
import { ApiError } from '@/services/apiClient'

export function notifySuccess(message: string, description?: string): void {
  toast.success(message, description ? { description } : undefined)
}

export function notifyInfo(message: string, description?: string): void {
  toast.info(message, description ? { description } : undefined)
}

export function notifyError(message: string, description?: string): void {
  toast.error(message, description ? { description } : undefined)
}

export function notifyRequestError(error: unknown, fallback: string): void {
  if (error instanceof ApiError && error.status < 500) {
    notifyError(error.message)
    return
  }

  if (error instanceof Error && !(error instanceof ApiError)) {
    notifyError(error.message || fallback)
    return
  }

  notifyError(fallback)
}
