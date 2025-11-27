export type AITool = 'summary' | 'flashcards' | 'mcq' | 'explain'

export interface AICacheEntry<T = any> {
  materialId: number
  tool: AITool
  content: T
  meta: {
    createdAt: string
    model?: string
    params?: Record<string, any>
  }
}

const PREFIX = 'smartstudy_ai_'

function key(materialId: number, tool: AITool) {
  return `${PREFIX}${materialId}_${tool}`
}

/**
 * saveCache stores a generated AI result into localStorage.
 * It overwrites any existing entry for the same material/tool.
 */
export function saveCache<T>(materialId: number, tool: AITool, content: T, meta?: Partial<AICacheEntry['meta']>) {
  const entry: AICacheEntry<T> = {
    materialId,
    tool,
    content,
    meta: {
      createdAt: new Date().toISOString(),
      ...(meta || {}),
    },
  }
  try { localStorage.setItem(key(materialId, tool), JSON.stringify(entry)) } catch {}
  return entry
}

/**
 * loadCache retrieves a cached AI result, or null if not present or invalid.
 */
export function loadCache<T = any>(materialId: number, tool: AITool): AICacheEntry<T> | null {
  try {
    const raw = localStorage.getItem(key(materialId, tool))
    if (!raw) return null
    const parsed = JSON.parse(raw) as AICacheEntry<T>
    if (!parsed || parsed.materialId !== materialId || parsed.tool !== tool) return null
    return parsed
  } catch {
    return null
  }
}

/**
 * clearCache removes the cache entry for a material/tool pair.
 */
export function clearCache(materialId: number, tool: AITool) {
  try { localStorage.removeItem(key(materialId, tool)) } catch {}
}

/**
 * humanTime returns a human-readable label for an ISO timestamp (e.g., "5m ago").
 */
export function humanTime(iso: string): string {
  const then = new Date(iso).getTime()
  const now = Date.now()
  const diff = Math.max(0, Math.floor((now - then) / 1000))
  if (diff < 60) return `${diff}s ago`
  const m = Math.floor(diff / 60)
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  const d = Math.floor(h / 24)
  return `${d}d ago`
}
