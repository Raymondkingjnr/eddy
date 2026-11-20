<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Bell, LogOut, User } from 'lucide-vue-next'
import UserAvatar from '@/components/avatar.vue'
import { useAuth } from '@/composables/useAuth'
import { notifyInfo, notifyRequestError } from '@/services/notifications'

const PROJECT_NAME = 'Lesson Creator'

const auth = useAuth()
const router = useRouter()
const user = auth.user

const isOpen = ref(false)
const root = ref<HTMLElement | null>(null)
const trigger = ref<HTMLButtonElement | null>(null)
const menu = ref<HTMLElement | null>(null)

function menuItems(): HTMLButtonElement[] {
  return Array.from(menu.value?.querySelectorAll<HTMLButtonElement>('[role="menuitem"]') ?? [])
}

async function toggle(): Promise<void> {
  isOpen.value = !isOpen.value
  if (isOpen.value) {
    await nextTick()
    menuItems()[0]?.focus()
  }
}

function closeAndRestoreFocus(): void {
  isOpen.value = false
  trigger.value?.focus()
}

function onDocumentPointerDown(event: PointerEvent): void {
  if (isOpen.value && root.value && !root.value.contains(event.target as Node)) {
    isOpen.value = false
  }
}

function onDocumentKeydown(event: KeyboardEvent): void {
  if (event.key === 'Escape' && isOpen.value) closeAndRestoreFocus()
}

function onMenuKeydown(event: KeyboardEvent): void {
  const list = menuItems()
  if (list.length === 0) return
  const index = list.indexOf(document.activeElement as HTMLButtonElement)

  if (event.key === 'ArrowDown') {
    event.preventDefault()
    list[(index + 1) % list.length]?.focus()
  } else if (event.key === 'ArrowUp') {
    event.preventDefault()
    list[(index - 1 + list.length) % list.length]?.focus()
  } else if (event.key === 'Home') {
    event.preventDefault()
    list[0]?.focus()
  } else if (event.key === 'End') {
    event.preventDefault()
    list[list.length - 1]?.focus()
  } else if (event.key === 'Tab') {
    isOpen.value = false
  }
}

function openProfile(): void {
  isOpen.value = false
  notifyInfo('Profile is coming soon')
}

function openNotifications(): void {
  isOpen.value = false
  notifyInfo('Notifications are coming soon')
}

async function handleLogout(): Promise<void> {
  isOpen.value = false
  try {
    await auth.logout()
    notifyInfo('You have been signed out')
  } catch (error) {
    notifyRequestError(error, 'The server could not end your session.')
  }
  await router.replace('/login')
}

onMounted(() => {
  document.addEventListener('pointerdown', onDocumentPointerDown)
  document.addEventListener('keydown', onDocumentKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', onDocumentPointerDown)
  document.removeEventListener('keydown', onDocumentKeydown)
})
</script>

<template>
  <div ref="root" class="relative">
    <button
      ref="trigger"
      type="button"
      class="rounded-full focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-(color:--color-primary)"
      aria-haspopup="menu"
      aria-controls="user-menu"
      aria-label="Open account menu"
      :aria-expanded="isOpen"
      @click="toggle"
    >
      <UserAvatar :fullname="user?.fullname" class="size-9 text-xs" />
    </button>

    <div
      v-if="isOpen"
      id="user-menu"
      ref="menu"
      role="menu"
      aria-label="Account"
      class="absolute top-[calc(100%+8px)] right-0 z-50 w-64 rounded-(--radius-card) border border-(color:--color-border) bg-(--color-surface) shadow-[0_12px_32px_rgba(16,24,40,0.12)]"
      @keydown="onMenuKeydown"
    >
      <div class="border-b border-(color:--color-border) px-4 py-3.5">
        <p class="text-sm font-bold text-(color:--color-foreground)">{{ PROJECT_NAME }}</p>
        <p class="mt-0.5 truncate text-[13px] text-(color:--color-muted)">{{ user?.fullname }}</p>
      </div>

      <div class="p-1.5">
        <button
          type="button"
          role="menuitem"
          class="flex h-10 w-full items-center gap-3 rounded-lg px-3 text-sm font-medium text-(color:--color-foreground) hover:bg-(--color-background) focus-visible:bg-(--color-background) focus-visible:outline-none"
          @click="openProfile"
        >
          <User class="size-4 shrink-0 text-(color:--color-muted)" aria-hidden="true" />
          Profile
        </button>
        <button
          type="button"
          role="menuitem"
          class="flex h-10 w-full items-center gap-3 rounded-lg px-3 text-sm font-medium text-(color:--color-foreground) hover:bg-(--color-background) focus-visible:bg-(--color-background) focus-visible:outline-none"
          @click="openNotifications"
        >
          <Bell class="size-4 shrink-0 text-(color:--color-muted)" aria-hidden="true" />
          Notification
        </button>
      </div>

      <div class="border-t border-(color:--color-border) p-1.5">
        <button
          type="button"
          role="menuitem"
          class="flex h-10 w-full items-center gap-3 rounded-lg px-3 text-sm font-semibold text-(color:--color-danger) hover:bg-(--color-danger-soft) focus-visible:bg-(--color-danger-soft) focus-visible:outline-none"
          @click="handleLogout"
        >
          <LogOut class="size-4 shrink-0" aria-hidden="true" />
          Sign out
        </button>
      </div>
    </div>
  </div>
</template>
