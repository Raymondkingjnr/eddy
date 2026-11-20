import { onBeforeUnmount, onMounted, ref } from 'vue'
import { createStatsService } from '@/services/stats-service'
import { notifyRequestError } from '@/services/notifications'
import type { Stats } from '@/types/stat'

const statsService = createStatsService()

export function useStats() {
  const stats = ref<Stats | null>(null)
  const isLoading = ref(false)
  const hasError = ref(false)
  let controller: AbortController | null = null

  async function load(): Promise<void> {
    // Cancel any in-flight request so an older response can't overwrite newer state.
    controller?.abort()
    const current = new AbortController()
    controller = current
    isLoading.value = true
    hasError.value = false

    try {
      const result = await statsService.getStats(current.signal)
      if (current.signal.aborted) return
      stats.value = result
    } catch (error) {
      if (current.signal.aborted) return
      hasError.value = true
      notifyRequestError(error, 'We could not load your statistics.')
    } finally {
      if (controller === current) isLoading.value = false
    }
  }

  onMounted(load)
  onBeforeUnmount(() => controller?.abort())

  return { stats, isLoading, hasError, load }
}
