import { describe, it, expect, beforeEach } from 'vitest'
import { saveCache, loadCache, clearCache } from './cache'

describe('cache utils', () => {
  beforeEach(() => localStorage.clear())

  it('saves and loads summary cache', () => {
    const entry = saveCache(1, 'summary', 'hello world')
    const loaded = loadCache<string>(1, 'summary')
    expect(loaded?.content).toBe('hello world')
    expect(loaded?.meta.createdAt).toBeDefined()
  })

  it('overwrites existing cache', () => {
    saveCache(2, 'mcq', [{ q: 'A' }])
    saveCache(2, 'mcq', [{ q: 'B' }])
    const loaded = loadCache<any[]>(2, 'mcq')
    expect(loaded?.content?.[0]?.q).toBe('B')
  })

  it('clears cache', () => {
    saveCache(3, 'flashcards', [{ question: 'Q', answer: 'A' }])
    clearCache(3, 'flashcards')
    const loaded = loadCache(3, 'flashcards')
    expect(loaded).toBeNull()
  })
})
