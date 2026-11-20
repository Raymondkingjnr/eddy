<script setup lang="ts">
import RoundedCard from './RoundedCard.vue'
</script>

<template>
  <RoundedCard>
    <div v-if="$slots.header" class="p-4 font-medium text-sm border-b border-gray-200">
      <slot name="header"></slot>
    </div>

    <div class="p-4 font-medium text-sm border-b border-gray-200">
      <slot></slot>
    </div>

    <div v-if="$slots.footer">
      <slot name="footer"></slot>
    </div>
  </RoundedCard>
</template>
