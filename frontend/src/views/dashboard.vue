<script setup lang="ts">
import { computed } from 'vue'
import {
  Bell,
  CircleCheck,
  Clock3,
  Flame,
  Library,
  PanelLeftClose,
  PanelLeftOpen,
  Plus,
  Search,
  Brain,
} from 'lucide-vue-next'
import AppSidebar from '@/layout/app-sidebar.vue'
import StatCard from '@/components/stat-card.vue'
import UserMenu from '@/layout/user-menu.vue'
import { useAuth } from '@/composables/useAuth'
import { useSidebar } from '@/composables/user-sidebar'
import { useStats } from '@/composables/useStats'
import { notifyInfo } from '@/services/notifications'
import { formatDuration, getGreeting } from '@/utils/format'
import BaseButton from '@/components/Button.vue'

defineOptions({ name: 'DashboardView' })

const { user } = useAuth()
const { collapsed, toggle } = useSidebar()
const { stats, isLoading, hasError, load } = useStats()

const firstName = computed(() => user.value?.fullname?.trim().split(/\s+/)[0] ?? '')
const greeting = computed(() => getGreeting(new Date()))

const subtitle = computed(() => {
  const days = stats.value?.streak_days ?? 0
  return days > 0
    ? `You’re on a ${days}-day learning streak. Keep the momentum going.`
    : 'Create a lesson and start learning today.'
})

// Skeletons only on the first load; a refresh keeps showing the previous numbers.
const showSkeleton = computed(() => isLoading.value && stats.value === null)

const cards = computed(() => {
  const s = stats.value
  return [
    {
      label: 'Lessons created',
      icon: Library,
      color: 'indigo' as const,
      value: s ? String(s.total_lessons) : '—',
      note: !s
        ? ''
        : s.total_lessons === 0
          ? 'Create your first lesson'
          : `${s.completed_lessons} completed`,
    },
    {
      label: 'Learning time',
      icon: Clock3,
      color: 'blue' as const,
      value: s ? formatDuration(s.time_spent) : '—',
      note: !s ? '' : s.time_spent === 0 ? 'Your journey starts here' : 'From completed topics',
    },
    {
      label: 'Topics completed',
      icon: CircleCheck,
      color: 'emerald' as const,
      value: s ? String(s.topics_completed) : '—',
      note: !s ? '' : s.topics_completed === 0 ? 'No topics completed yet' : 'Keep it going',
    },
    {
      label: 'Current streak',
      icon: Flame,
      color: 'orange' as const,
      value: s ? `${s.streak_days} ${s.streak_days === 1 ? 'day' : 'days'}` : '—',
      note: !s ? '' : s.streak_days === 0 ? 'Complete a topic to start' : 'Keep the momentum going',
    },
  ]
})
</script>

<template>
  <div class="flex min-h-screen bg-(--color-background)">
    <AppSidebar :collapsed="collapsed" />

    <div class="flex min-w-0 flex-1 flex-col">
      <header
        class="flex h-[68px] shrink-0 items-center justify-between gap-4 border-b border-(color:--color-border) bg-(--color-surface) px-8"
      >
        <div class="flex items-center gap-3">
          <button
            type="button"
            class="flex size-9 items-center justify-center rounded-(--radius-control) text-(color:--color-muted) hover:bg-(--color-background) focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-(color:--color-primary)"
            :aria-label="collapsed ? 'Expand sidebar' : 'Collapse sidebar'"
            :aria-pressed="collapsed"
            @click="toggle"
          >
            <PanelLeftOpen v-if="collapsed" class="size-4.5" aria-hidden="true" />
            <PanelLeftClose v-else class="size-[18px]" aria-hidden="true" />
          </button>
          <p class="text-base font-medium text-(--color-foreground)">Dashboard</p>
        </div>

        <div class="flex items-center gap-3">
          <label
            class="hidden h-9 w-65 items-center gap-2 rounded-(--radius-control) border border-(--color-border) bg-(--color-background) px-3 md:flex"
          >
            <Search class="size-3.75 shrink-0 text-(--color-subtle)" aria-hidden="true" />
            <input
              type="search"
              disabled
              placeholder="Search lessons"
              title="Search is coming soon"
              class="min-w-0 flex-1 bg-transparent text-[13px] rounded-2xl outline-none placeholder:text-(--color-subtle)"
            />
            <!-- <span class="text-[11px] text-(color:--color-subtle)" aria-hidden="true">⌘ K</span> -->
          </label>

          <button
            type="button"
            class="flex size-9 items-center justify-center rounded-(--radius-control) border border-(--color-border) bg-(--color-surface) text-(--color-muted) hover:bg-(--color-background) focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-(--color-primary)"
            aria-label="Notifications"
            @click="notifyInfo('Notifications are coming soon')"
          >
            <Bell class="size-4.25" aria-hidden="true" />
          </button>

          <UserMenu />
        </div>
      </header>

      <main class="flex flex-col gap-7 p-8">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="flex flex-col gap-[5px]">
            <h1 class="text-[24px] font-medium text-(--color-foreground)">
              {{ greeting }}<template v-if="firstName">, {{ firstName }}</template>
            </h1>
            <p class="text-sm text-(--color-muted)">{{ subtitle }}</p>
          </div>

          <div class="flex gap-2.5">
            <BaseButton
              type="button"
              variant="secondary"
              size="lg"
              :icon="Plus"
              @click="notifyInfo('Manual lesson creation is coming soon')"
            >
              Create manually
            </BaseButton>
            <BaseButton
              type="button"
              variant="primary"
              size="lg"
              :icon="Brain"
              @click="notifyInfo('AI lesson creation is coming soon')"
            >
              Create with AI
            </BaseButton>
          </div>
        </div>

        <section aria-label="Statistics" class="flex flex-col gap-3">
          <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard
              v-for="card in cards"
              :key="card.label"
              :label="card.label"
              :value="card.value"
              :note="card.note"
              :icon="card.icon"
              :loading="showSkeleton"
              :color="card.color"
            />
          </div>
          <button
            v-if="hasError"
            type="button"
            class="self-start text-[13px] font-semibold text-(--color-primary) hover:underline"
            @click="load"
          >
            Retry loading statistics
          </button>
        </section>
      </main>
    </div>
  </div>
</template>
