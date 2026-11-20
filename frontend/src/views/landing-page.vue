<script setup lang="ts">
import BookingItem from '@/components/BookingItem.vue'
import CourseItem from '@/components/CourseItem.vue'
import Sekeleton from '@/components/sekeleton.vue'
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { createDemoCatalogService } from '@/services/demoCatalogService'
import { notifyInfo, notifyRequestError, notifySuccess } from '@/services/notifications'
import type { DemoBooking, DemoCourse } from '@/types/demoCatalog'

const catalog = createDemoCatalogService()
const courses = ref<DemoCourse[]>([])
const bookings = ref<DemoBooking[]>([])
const loading = ref(false)
const bookingsLoading = ref(false)

const fetchCourses = async () => {
  try {
    loading.value = true
    courses.value = await catalog.getCourses()
  } catch (error) {
    notifyRequestError(error, 'Unable to load courses right now.')
  } finally {
    loading.value = false
  }
}

const fetchBookings = async () => {
  try {
    bookingsLoading.value = true
    bookings.value = await catalog.getBookings()
  } catch (error) {
    notifyRequestError(error, 'Unable to load your courses right now.')
  } finally {
    bookingsLoading.value = false
  }
}

const purchaseCourse = async (course: DemoCourse) => {
  if (bookings.value?.some((b) => b.id === course.id)) {
    notifyInfo('Course already added')
    return
  }

  try {
    const booking = await catalog.createBooking(course)
    bookings.value = [...bookings.value.filter((item) => item.id !== booking.id), booking]
    notifySuccess('Course added to your learning list')
  } catch (error) {
    notifyRequestError(error, 'Unable to add this course right now.')
  }
}

onMounted(() => {
  void fetchCourses()
  void fetchBookings()
})
</script>

<template>
  <div class="p-4">
    <header class="flex items-center justify-between gap-4">
      <h1 class="text-4xl font-medium">Lesson Mentor</h1>
      <nav class="flex gap-4 text-sm font-semibold text-indigo-600" aria-label="Account">
        <RouterLink to="/login" class="hover:underline">Log in</RouterLink>
        <RouterLink to="/register" class="hover:underline">Create account</RouterLink>
      </nav>
    </header>
    <p class="mt-2 text-gray-600">Course catalog prototype</p>
    <h2 class="text-2xl font-medium mb-2 mt-12">All Course</h2>

    <div v-if="loading" class="grid gap-4 md:grid-cols-2">
      <Sekeleton v-for="index in 4" :key="index">
        <template #header> </template>
        <template #footer>
          <div class="bg-gray-300 rounded-full h-8 w-36"></div>
          <div class="bg-gray-300 rounded-full h-6 w-18"></div>
        </template>
      </Sekeleton>
    </div>

    <div v-else class="space-y-2.5 grid gap-4 md:grid-cols-3">
      <CourseItem
        v-for="course in courses"
        :key="course.id"
        :title="course.title"
        :description="course.description"
        :price="course.price"
        @click="purchaseCourse(course)"
      />
    </div>
    <h2 class="text-2xl font-medium mb-2 mt-6">Your Courses</h2>

    <div v-if="bookingsLoading" class="grid gap-4 md:grid-cols-2">
      <Sekeleton v-for="index in 2" :key="index">
        <template #footer>
          <div class="bg-gray-300 rounded-full h-8 w-36"></div>
          <div class="bg-gray-300 rounded-full h-6 w-18"></div>
        </template>
      </Sekeleton>
    </div>

    <div v-else class="grid grid-cols-2 gap-4">
      <BookingItem
        v-for="booking in bookings"
        :key="booking.id"
        :title="booking.title"
        :status="booking.status"
      />
    </div>
  </div>
</template>
