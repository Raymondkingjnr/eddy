<script setup lang="ts">
import { computed } from 'vue'
import { getInitials } from '@/utils/format'

const props = defineProps<{ fullname?: string | null }>()
const initials = computed(() => getInitials(props.fullname))
</script>

<template>
  <div
    class="flex shrink-0 items-center justify-center rounded-full bg-(--color-avatar) font-semibold text-(color:--color-avatar-foreground)"
    aria-hidden="true"
  >
    {{ initials }}
  </div>
</template>
