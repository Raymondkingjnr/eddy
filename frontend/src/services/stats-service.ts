import { apiClient, type ApiClient } from '@/services/apiClient'
import type { Stats } from '@/types/stat'

export function createStatsService(api: ApiClient = apiClient) {
  return {
    async getStats(signal?: AbortSignal): Promise<Stats> {
      return api<Stats>('/stats', { signal })
    },
  }
}
