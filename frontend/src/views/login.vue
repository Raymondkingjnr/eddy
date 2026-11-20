<script setup lang="ts">
import { ref, watch } from 'vue'
import AuthLayout from '@/components/auth-layout.vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { notifyInfo, notifyRequestError, notifySuccess } from '@/services/notifications'

defineOptions({ name: 'LoginView' })

const router = useRouter()
const route = useRoute()
const auth = useAuth()
const initializationError = auth.initializationError
const email = ref('')
const password = ref('')
const isSubmitting = ref(false)

if (route.query.logoutError === 'true') {
  notifyInfo('Signed out on this device', 'The server could not be reached to end the session.')
}

watch(
  initializationError,
  (message) => {
    if (message) notifyRequestError(new Error(message), 'Unable to verify your session.')
  },
  { immediate: true },
)

async function handleLogin() {
  isSubmitting.value = true

  try {
    await auth.login({ email: email.value, password: password.value })
    notifySuccess('Welcome back')
    const redirect = route.query.redirect
    const destination =
      typeof redirect === 'string' && redirect.startsWith('/') && !redirect.startsWith('//')
        ? redirect
        : '/dashboard'
    await router.replace(destination)
  } catch (error) {
    notifyRequestError(error, 'Unable to sign in. Please try again.')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <AuthLayout>
    <!-- <p class="mb-2 text-xs font-bold tracking-wide text-indigo-600">WELCOME BACK</p> -->
    <h2 class="mb-2 text-[18px] font-medium text-gray-900">Log in to Lesson Mentor</h2>
    <p class="mb-6 text-sm font-light text-gray-800">
      Continue creating and managing your lessons.
    </p>

    <p v-if="initializationError" class="mb-4 text-sm text-red-700" role="alert">
      {{ initializationError }}
    </p>

    <form @submit.prevent="handleLogin">
      <label for="email" class="label"> Email address </label>
      <input id="email" v-model="email" type="email" autocomplete="email" class="input mb-6" />

      <label for="password" class="label"> Password </label>
      <input
        id="password"
        v-model="password"
        type="password"
        autocomplete="current-password"
        class="input"
      />

      <button
        type="submit"
        :disabled="isSubmitting"
        class="mt-5 w-full rounded-2xl bg-indigo-600 py-3 text-sm text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-60"
      >
        {{ isSubmitting ? 'Signing in…' : 'Log in' }}
      </button>
    </form>

    <p class="mt-5 text-center text-[13px] text-gray-500">
      New to Lesson Mentor?
      <RouterLink to="/register" class="font-normal text-indigo-600 hover:underline pl-1"
        >Create an account
      </RouterLink>
    </p>
  </AuthLayout>
</template>
