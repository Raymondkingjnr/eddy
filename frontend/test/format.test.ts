import { describe, expect, it } from 'vitest'
import { formatDuration, getGreeting, getInitials } from '@/utils/format'

describe('formatDuration', () => {
  it('shows minutes under an hour', () => {
    expect(formatDuration(0)).toBe('0 min')
    expect(formatDuration(45)).toBe('45 min')
  })

  it('shows hours and minutes', () => {
    expect(formatDuration(504)).toBe('8h 24m')
    expect(formatDuration(120)).toBe('2h')
  })

  it('clamps negative values to zero', () => {
    expect(formatDuration(-5)).toBe('0 min')
  })
})

describe('getInitials', () => {
  it('uses first and last name', () => {
    expect(getInitials('Maya Chen')).toBe('MC')
    expect(getInitials('  maya   anne  chen ')).toBe('MC')
  })

  it('handles a single name and empty values', () => {
    expect(getInitials('Maya')).toBe('M')
    expect(getInitials('')).toBe('?')
    expect(getInitials(null)).toBe('?')
  })
})

describe('getGreeting', () => {
  it('follows the time of day', () => {
    expect(getGreeting(new Date(2026, 0, 1, 8))).toBe('Good morning')
    expect(getGreeting(new Date(2026, 0, 1, 14))).toBe('Good afternoon')
    expect(getGreeting(new Date(2026, 0, 1, 20))).toBe('Good evening')
  })
})
