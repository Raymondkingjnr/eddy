<script setup lang="ts">
import type { Component } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import {
  BookOpen,
  BookOpenCheck,
  CircleCheck,
  LayoutDashboard,
  Settings,
  Brain,
} from 'lucide-vue-next'
import UserAvatar from '@/components/avatar.vue'
import { useAuth } from '@/composables/useAuth'
import { notifyInfo } from '@/services/notifications'

interface NavItem {
  label: string
  icon: Component
  /** Items without a route are placeholders until their screens exist. */
  to?: string
}

defineProps<{ collapsed: boolean }>()

const route = useRoute()
const { user } = useAuth()

const items: NavItem[] = [
  { label: 'Dashboard', icon: LayoutDashboard, to: '/dashboard' },
  { label: 'Create with AI', icon: Brain },
  { label: 'My lessons', icon: BookOpen },
  { label: 'Completed', icon: CircleCheck },
  { label: 'Settings', icon: Settings },
]

function isActive(item: NavItem): boolean {
  return item.to !== undefined && route.path === item.to
}

function itemClasses(active: boolean, collapsed: boolean): string[] {
  return [
    'flex h-[42px] w-full items-center rounded-lg font-normal text-sm transition-colors',
    'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-(color:--color-primary)',
    collapsed ? 'justify-center' : 'gap-[11px] px-3',
    active
      ? 'bg-(--color-primary-soft) font-normal text-(color:--color-primary-strong)'
      : 'font-medium text-(color:--color-muted) hover:bg-(--color-background) hover:text-(color:--color-foreground)',
  ]
}
</script>

<template>
  <aside
    class="sticky top-0 flex h-screen shrink-0 flex-col justify-between overflow-hidden border-r border-(color:--color-border) bg-(--color-surface) py-6 transition-[width] duration-200"
    :class="collapsed ? 'w-[72px] px-3' : 'w-[228px] px-[18px]'"
  >
    <div class="flex flex-col gap-7">
      <div class="flex items-center gap-2.5" :class="collapsed ? 'justify-center' : 'px-2'">
        <div
          class="flex size-[30px] shrink-0 items-center justify-center rounded-lg bg-(--color-primary)"
        >
          <BookOpenCheck class="size-[17px] text-white" aria-hidden="true" />
        </div>
        <span
          v-if="!collapsed"
          class="text-base font-medium whitespace-nowrap text-(color:--color-foreground)"
        >
          Lesson Creator
        </span>
      </div>

      <nav aria-label="Primary">
        <ul class="flex flex-col gap-[5px]">
          <li v-for="item in items" :key="item.label">
            <RouterLink
              v-if="item.to"
              :to="item.to"
              :class="itemClasses(isActive(item), collapsed)"
              :aria-current="isActive(item) ? 'page' : undefined"
              :aria-label="collapsed ? item.label : undefined"
              :title="collapsed ? item.label : undefined"
            >
              <component :is="item.icon" class="size-[18px] shrink-0" aria-hidden="true" />
              <span v-if="!collapsed" class="whitespace-nowrap">{{ item.label }}</span>
            </RouterLink>
            <button
              v-else
              type="button"
              :class="itemClasses(false, collapsed)"
              :aria-label="collapsed ? item.label : undefined"
              :title="collapsed ? item.label : undefined"
              @click="notifyInfo(`${item.label} is coming soon`)"
            >
              <component :is="item.icon" class="size-[18px] shrink-0" aria-hidden="true" />
              <span v-if="!collapsed" class="whitespace-nowrap">{{ item.label }}</span>
            </button>
          </li>
        </ul>
      </nav>
    </div>

    <div
      class="flex items-center gap-2.5 border-t border-(color:--color-border) pt-4"
      :class="collapsed ? 'justify-center' : 'px-2'"
      :title="collapsed ? (user?.fullname ?? undefined) : undefined"
    >
      <UserAvatar :fullname="user?.fullname" class="size-8 text-xs" />
      <div v-if="!collapsed" class="min-w-0">
        <p class="truncate text-[13px] font-semibold text-(color:--color-foreground)">
          {{ user?.fullname }}
        </p>
        <p class="truncate text-xs text-(color:--color-muted)">{{ user?.email }}</p>
      </div>
    </div>
  </aside>
</template>
