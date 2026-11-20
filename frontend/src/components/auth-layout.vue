<script setup lang="ts">
defineProps({
  brandName: {
    type: String,
    default: 'Lesson Mentor',
  },
  badge: {
    type: String,
    default: 'AI-Powered Learning',
  },
  headline: {
    type: String,
    default: 'Turn any goal into a lesson you can finish.',
  },
  subheadline: {
    type: String,
    default: 'Structured explanations, practical examples, and progress that keeps you moving.',
  },
  course: {
    type: Object,
    default: () => ({
      title: 'Python for AI Engineering',
      meta: '6 topics · 48 min',
      progress: 67,
      topics: [
        { label: 'Python data flow', done: true },
        { label: 'NumPy foundations', done: false },
        { label: 'Build a tiny model', done: false },
      ],
    }),
  },

  testimonial: {
    type: Object,
    default: () => ({
      quote: 'I built a focused learning path in minutes, then actually completed it.',
      name: 'Ari Patel',
      role: 'ML Platform Engineer',
    }),
  },
})
</script>

<template>
  <div class="grid min-h-screen grid-cols-1 md:grid-cols-12 font-sans bg-white">
    <!-- LEFT: custom per screen -->
    <div class="flex flex-col bg-neutral-50 px-6 py-12 md:px-36 md:py-16 md:col-span-7">
      <div
        class="mx-auto my-auto flex w-full max-w-100 flex-col items-center justify-center rounded-md border border-gray-50 bg-white p-8 shadow"
      >
        <div class="mb-5 flex items-center gap-2.5">
          <span
            class="grid h-7 w-7 shrink-0 place-items-center rounded-md bg-indigo-600 text-white"
          >
            <svg
              viewBox="0 0 24 24"
              width="20"
              height="20"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <path
                d="M12 4v16M4 6c4-2 8-2 8 0v14c0-2-4-2-8 0V6zM20 6c-4-2-8-2-8 0v14c0-2 4-2 8 0V6z"
              />
            </svg>
          </span>
          <!-- <span class="text-[15px] font-medium text-gray-900">{{ brandName }}</span> -->
        </div>
        <slot />
      </div>
    </div>

    <!-- RIGHT: shared across every auth screen -->
    <div
      class="hidden items-center m-2 rounded-lg bg-[#3730A3] px-16 py-12 text-white md:flex md:col-span-5"
    >
      <div class="max-w-120">
        <p class="mb-4 flex items-center gap-2 text-[13px] font-medium text-indigo-200">
          <span class="text-indigo-300">✦</span>
          {{ badge }}
        </p>

        <h1 class="mb-4 text-[34px] font-medium leading-tight">{{ headline }}</h1>
        <p class="mb-10 text-[15px] leading-relaxed font-light text-indigo-100">
          {{ subheadline }}
        </p>

        <div class="mb-10 rounded-2xl border border-white/10 bg-white/8 p-5">
          <div class="mb-4 flex items-center gap-3">
            <span
              class="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-indigo-500 text-[12px]"
            >
              &lt;/&gt;
            </span>
            <div class="flex-1">
              <p class="text-sm font-semibold">{{ course.title }}</p>
              <p class="mt-0.5 text-xs text-indigo-200">{{ course.meta }}</p>
            </div>
            <span class="text-[13px] font-semibold text-indigo-100">{{ course.progress }}%</span>
          </div>

          <ul class="flex flex-col gap-2">
            <li
              v-for="(topic, i) in course.topics"
              :key="i"
              class="flex items-center gap-2.5 rounded-lg bg-white/5 px-3 py-2.5 text-[13px] text-indigo-100"
            >
              <span
                class="h-3.5 w-3.5 shrink-0 rounded-full border-2"
                :class="topic.done ? 'border-indigo-300 bg-indigo-300' : 'border-white/40'"
              />
              {{ topic.label }}
            </li>
          </ul>
        </div>

        <blockquote>
          <p class="mb-4 text-[15px] italic leading-relaxed text-indigo-50">
            &ldquo;{{ testimonial.quote }}&rdquo;
          </p>
          <footer class="flex items-center gap-2.5">
            <span class="h-8 w-8 shrink-0 rounded-full bg-white/25" />
            <div>
              <p class="text-[13px] font-semibold">{{ testimonial.name }}</p>
              <p class="mt-0.5 text-xs text-indigo-200">{{ testimonial.role }}</p>
            </div>
          </footer>
        </blockquote>
      </div>
    </div>
  </div>
</template>
