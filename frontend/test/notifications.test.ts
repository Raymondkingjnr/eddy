import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ApiError } from '@/services/apiClient'

const { toast } = vi.hoisted(() => ({
  toast: {
    error: vi.fn(),
    info: vi.fn(),
    success: vi.fn()
  }
}))

vi.mock('vue-sonner', () => ({ toast }))

import {
  notifyError,
  notifyInfo,
  notifyRequestError,
  notifySuccess
} from '@/services/notifications'

describe('notifications', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('uses the matching vue-sonner method for success, info, and error messages', () => {
    notifySuccess('Saved', 'Your lesson is ready.')
    notifyInfo('Draft only')
    notifyError('Could not save')

    expect(toast.success).toHaveBeenCalledWith('Saved', { description: 'Your lesson is ready.' })
    expect(toast.info).toHaveBeenCalledWith('Draft only', undefined)
    expect(toast.error).toHaveBeenCalledWith('Could not save', undefined)
  })

  it('shows client and safe server request errors', () => {
    notifyRequestError(new Error('Network unavailable'), 'Request failed.')
    notifyRequestError(new ApiError('Email already registered', 400), 'Request failed.')

    expect(toast.error).toHaveBeenNthCalledWith(1, 'Network unavailable', undefined)
    expect(toast.error).toHaveBeenNthCalledWith(2, 'Email already registered', undefined)
  })

  it('uses a friendly fallback instead of exposing server failures', () => {
    notifyRequestError(new ApiError('Internal database trace', 500), 'Please try again later.')
    notifyRequestError('unexpected payload', 'Request failed.')

    expect(toast.error).toHaveBeenNthCalledWith(1, 'Please try again later.', undefined)
    expect(toast.error).toHaveBeenNthCalledWith(2, 'Request failed.', undefined)
  })
})
