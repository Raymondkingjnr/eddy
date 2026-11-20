import { ref } from 'vue'

const STORAGE_KEY = 'lesson-creator:sidebar-collapsed'

function readStored(): boolean {
  try {
    return localStorage.getItem(STORAGE_KEY) === 'true'
  } catch {
    return false
  }
}

const collapsed = ref(readStored())

export function useSidebar() {
  function toggle(): void {
    collapsed.value = !collapsed.value
    try {
      localStorage.setItem(STORAGE_KEY, String(collapsed.value))
    } catch {
      // Storage can be unavailable (private mode); the preference just won't persist.
    }
  }

  return { collapsed, toggle }
}
