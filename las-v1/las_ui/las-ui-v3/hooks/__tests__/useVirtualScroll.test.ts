import { renderHook } from '@testing-library/react'
import { useVirtualScroll } from '../use-virtual-scroll'
import { describe, it, expect } from 'vitest'

describe('useVirtualScroll', () => {
  it('initializes with correct properties', () => {
    const { result } = renderHook(() => useVirtualScroll({
      count: 100,
      estimateSize: () => 50,
    }))

    expect(result.current.rowVirtualizer).toBeDefined()
    expect(result.current.parentRef).toBeDefined()
    expect(result.current.scrollToEnd).toBeDefined()
  })

  // Since we are wrapping tanstack virtual, we mostly trust it works.
  // We want to test our autoScroll logic if possible.
  // However, testing scroll behavior in JSDOM is tricky because layout/measurement often doesn't work as expected without mocking.
  
  it('returns a ref object', () => {
    const { result } = renderHook(() => useVirtualScroll({
      count: 10,
      estimateSize: () => 30,
    }))
    expect(result.current.parentRef.current).toBeNull()
  })
})
