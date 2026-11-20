import type { DemoBooking, DemoCourse } from '@/types/demoCatalog'

const demoApiBaseUrl = 'http://localhost:3001'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${demoApiBaseUrl}${path}`, options)

  if (!response.ok) {
    throw new Error(`The demo catalog request failed with status ${response.status}.`)
  }

  return response.json() as Promise<T>
}

export function createDemoCatalogService() {
  return {
    getCourses(): Promise<DemoCourse[]> {
      return request<DemoCourse[]>('/courses')
    },

    getBookings(): Promise<DemoBooking[]> {
      return request<DemoBooking[]>('/bookings')
    },

    createBooking(course: DemoCourse): Promise<DemoBooking> {
      return request<DemoBooking>('/bookings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...course, status: 'confirmed' })
      })
    }
  }
}
