<script setup lang="ts">
import { ref } from 'vue'
import AuthLayout from '@/components/auth-layout.vue'
import { RouterLink, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { notifyRequestError, notifySuccess } from '@/services/notifications'

defineOptions({ name: 'RegisterView' })

const router = useRouter()
const auth = useAuth()
const email = ref('')
const fullname = ref('')
const password = ref('')
const isSubmitting = ref(false)

async function handleRegister() {
  isSubmitting.value = true

  try {
    await auth.register({ email: email.value, password: password.value, fullname: fullname.value })
    notifySuccess('Account created', 'Welcome to Lesson Mentor.')
    await router.replace('/dashboard')
  } catch (error) {
    notifyRequestError(error, 'Unable to create your account. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <AuthLayout>
    <!-- <p class="mb-2 text-xs font-bold tracking-wide text-indigo-600">START LEARNING</p> -->
    <h2 class="mb-2 text-[20px] font-medium text-gray-900">Create your account</h2>
    <p class="mb-6 text-sm leading-4 font-light text-gray-800">
      Build personalized lessons and learn at your own pace.
    </p>

    <form @submit.prevent="handleRegister">
      <label for="fullname" class="label"> Full name </label>
      <input
        id="fullname"
        v-model="fullname"
        type="text"
        autocomplete="name"
        required
        class="mb-4 input"
      />
      <label for="email" class="label"> Email address </label>
      <input
        id="email"
        v-model="email"
        type="email"
        autocomplete="email"
        required
        class="mb-4 input"
      />

      <label for="password" class="label"> Password </label>
      <input
        id="password"
        v-model="password"
        type="password"
        autocomplete="new-password"
        required
        class="input"
      />

      <button
        type="submit"
        :disabled="isSubmitting"
        class="mt-5 w-full rounded-2xl bg-indigo-600 py-3 text-sm text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {{ isSubmitting ? 'Creating account…' : 'Create account' }}
      </button>
    </form>

    <p class="mt-5 text-center text-[13px] text-gray-500">
      Already have an account?
      <RouterLink to="/login" class="font-normal text-indigo-600 pl-1.5 hover:underline"
        >Log in</RouterLink
      >
    </p>
  </AuthLayout>
</template>
