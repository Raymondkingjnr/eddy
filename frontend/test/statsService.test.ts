import { describe, expect, it, vi } from 'vitest'
import type { ApiClient } from '@/services/apiClient'
import { createStatsService } from '@/services/stats-service'
import type { Stats } from '@/types/stats'

const sample: Stats = {
  total_lessons: 2,
  completed_lessons: 1,
  in_progress_lessons: 1,
  draft_lessons: 0,
  topics_completed: 4,
  time_spent: 95,
  streak_days: 3,
}

describe('statsService', () => {
  it('requests GET /stats and returns the payload', async () => {
    const api = vi.fn().mockResolvedValue(sample)
    const service = createStatsService(api as unknown as ApiClient)
    const controller = new AbortController()

    await expect(service.getStats(controller.signal)).resolves.toEqual(sample)
    expect(api).toHaveBeenCalledWith('/stats', { signal: controller.signal })
  })

  it('propagates request failures', async () => {
    const api = vi.fn().mockRejectedValue(new Error('boom'))
    const service = createStatsService(api as unknown as ApiClient)

    await expect(service.getStats()).rejects.toThrow('boom')
  })
})
