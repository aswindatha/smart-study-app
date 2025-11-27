import { describe, it, expect, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useElapsed } from './useElapsed'

describe('useElapsed', () => {
  it('counts up every second from startISO', () => {
    vi.useFakeTimers()
    const start = new Date().toISOString()
    const { result } = renderHook(() => useElapsed(start))
    expect(result.current.seconds).toBe(0)
    act(() => { vi.advanceTimersByTime(1100) })
    expect(result.current.seconds).toBeGreaterThanOrEqual(1)
    vi.useRealTimers()
  })
})
