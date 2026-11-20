export interface Stats {
  total_lessons: number
  completed_lessons: number
  in_progress_lessons: number
  draft_lessons: number
  topics_completed: number
  /** Minutes, summed over completed topics. */
  time_spent: number
  streak_days: number
}
