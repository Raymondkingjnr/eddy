<script setup lang="ts">
import { RouterView } from 'vue-router'
import { Toaster } from 'vue-sonner'
import 'vue-sonner/style.css'
</script>

<template>
  <RouterView />
  <Toaster position="top-right" :duration="3000" :rich-colors="true" :close-button="true" />
</template>
