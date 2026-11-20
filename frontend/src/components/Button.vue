<script setup lang="ts">
import type { Component } from 'vue'

type Variant = 'default' | 'secondary' | 'primary' | 'danger'
type Size = 'sm' | 'lg'

const variants: Record<Variant, string> = {
  default: 'border border-gray-200 hover:bg-gray-100',
  secondary:
    'border border-(color:--color-border-strong) bg-(--color-surface) text-(color:--color-foreground) hover:bg-(--color-background)',
  primary: 'bg-(--color-primary) text-white hover:bg-(--color-primary-hover)',
  danger: 'bg-red-200 text-red-900 enabled:hover:bg-red-100',
}

// 'sm' is the original look, so existing usages are unchanged.
const sizes: Record<Size, string> = {
  sm: 'rounded-2xl font-light text-xs py-1 px-3',
  lg: 'h-10 rounded-2xl text-sm font-light px-[15px]',
}

const iconSizes: Record<Size, string> = {
  sm: 'size-3.5',
  lg: 'size-4',
}

withDefaults(
  defineProps<{
    variant?: Variant
    size?: Size
    /** Optional leading icon, e.g. a lucide component. */
    icon?: Component
  }>(),
  { variant: 'default', size: 'sm', icon: undefined },
)
</script>

<template>
  <!-- Attributes (type, disabled, aria-*, class) and the native click event fall through to the button. -->
  <button
    :class="[
      'inline-flex items-center justify-center gap-2 transition-colors  font-normal duration-300',
      'focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-(--color-primary)',
      'disabled:cursor-not-allowed disabled:opacity-50',
      sizes[size],
      variants[variant],
    ]"
  >
    <component :is="icon" v-if="icon" :class="['shrink-0', iconSizes[size]]" aria-hidden="true" />
    <slot />
  </button>
</template>
