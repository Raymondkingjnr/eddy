<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  label: string
  value: string
  note: string
  icon: Component
  color?: 'indigo' | 'blue' | 'emerald' | 'orange'
  loading?: boolean
}>()

const colorClasses = {
  indigo: {
    border: 'before:bg-indigo-500',
    icon: 'bg-indigo-50 text-indigo-600',
  },
  blue: {
    border: 'before:bg-sky-500',
    icon: 'bg-sky-50 text-sky-600',
  },
  emerald: {
    border: 'before:bg-emerald-500',
    icon: 'bg-emerald-50 text-emerald-600',
  },
  orange: {
    border: 'before:bg-orange-500',
    icon: 'bg-orange-50 text-orange-600',
  },
} as const
</script>

<template>
  <article
    :class="[
      'group relative flex items-start justify-between overflow-hidden',
      'rounded-(--radius-card) border border-(--color-border)',
      'bg-white p-[18px]',
      'shadow-[0_4px_16px_rgba(16,24,40,0.04)]',
      'transition-all duration-300 hover:-translate-y-1',
      'hover:shadow-[0_8px_24px_rgba(16,24,40,0.08)]',
      'before:absolute before:inset-x-0 before:top-0 before:h-[2px] before:content-[\'\']',
      colorClasses[color ?? 'indigo'].border,
    ]"
  >
    <div class="flex flex-col gap-2">
      <p class="text-[13px] font-medium text-(--color-muted)">
        {{ label }}
      </p>

      <div
        v-if="loading"
        class="h-[26px] w-20 animate-pulse rounded-md bg-(--color-border)"
        role="status"
        aria-label="Loading"
      />

      <p v-else class="text-[24px] leading-8 font-normal text-(--color-foreground)">
        {{ value }}
      </p>

      <p class="min-h-4 text-xs text-(--color-muted)">
        {{ loading ? '' : note }}
      </p>
    </div>

    <div
      :class="[
        'flex size-10 shrink-0 items-center justify-center',
        'rounded-(--radius-control)',
        'transition-transform duration-300 group-hover:scale-110',
        colorClasses[color ?? 'indigo'].icon,
      ]"
    >
      <component :is="icon" class="size-4.75" aria-hidden="true" />
    </div>
  </article>
</template>
