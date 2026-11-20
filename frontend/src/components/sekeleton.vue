<script setup lang="ts">
import RoundedCard from './RoundedCard.vue'
</script>

<template>
  <RoundedCard>
    <div v-if="$slots.header" class="h-36 rounded-t-md bg-gray-300 animate-pulse">
      <slot name="header" />
    </div>

    <div v-if="$slots.footer" class="flex justify-between items-center p-4">
      <slot name="footer" />
    </div>
  </RoundedCard>
</template>
