import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/dashboard.vue'
import register from '@/views/register.vue'
import login from '@/views/login.vue'
import landingPage from '@/views/landing-page.vue'
import { useAuth } from '@/composables/useAuth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing-page',
      component: landingPage,
      meta: {},
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: Dashboard,
      meta: { requiresAuth: true },
    },
    {
      path: '/login',
      name: 'login',
      component: login,
      meta: { guestOnly: true },
    },
    {
      path: '/register',
      name: 'register',
      component: register,
      meta: { guestOnly: true },
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuth()
  await auth.initialize()

  if (to.meta.requiresAuth && !auth.isAuthenticated.value) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }

  if (to.meta.guestOnly && auth.isAuthenticated.value) {
    return { name: 'dashboard' }
  }

  return true
})

export default router
