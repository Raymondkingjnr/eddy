<script setup lang="ts">
import Button from './Button.vue'
import CardSection from './CardSection.vue'

defineProps({
  title: String,
  status: String,
})
</script>

<template>
  <div>
    <CardSection>
      <div class="flex justify-between items-center">
        <p>{{ title }}</p>
        <p>{{ status }}</p>
        <Button variant="danger"> Report </Button>
      </div>
    </CardSection>
  </div>
</template>
