<script setup lang="ts">
import Button from './Button.vue'
import CardSection from './CardSection.vue'

defineProps({
  title: String,
  price: Number,
  description: String,
})

defineEmits(['click'])
</script>

<template>
  <CardSection>
    <template #header>{{ title }}</template>

    <template #default>${{ price }}</template>

    <template #footer>
      <p class="p-4 font-medium text-sm">
        {{ description }}
      </p>
      <div class="flex justify-end p-4">
        <Button @click="$emit('click')">Purchase</Button>
      </div>
    </template>
  </CardSection>
</template>
