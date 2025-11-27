import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { summarize, generateFlashcards, generateMCQ, explain, processMaterial } from '@/lib/api'
import Skeleton from '@/components/ui/skeleton'
import { toast } from 'sonner'
import { Clipboard, BadgeInfo } from 'lucide-react'
import Accordion, { AccordionItem } from '@/components/ui/Accordion'
import { saveCache, loadCache, clearCache, humanTime, type AITool } from '@/utils/cache'
import ToolControls from '@/components/ai/ToolControls'

function Copy({ text }: { text: string }) {
  return (
    <button
      className="text-xs text-blue-600 hover:underline inline-flex items-center gap-1"
      onClick={() => { navigator.clipboard.writeText(text); toast.success('Copied') }}
    >
      <Clipboard size={14} /> Copy
    </button>
  )
}

export default function AIToolsPanel({ materialId }: { materialId: number }) {
  const [extract, setExtract] = useState<string>('')
  const [loadingExtract, setLoadingExtract] = useState<boolean>(true)

  useEffect(() => {
    async function load() {
      setLoadingExtract(true)
      try {
        const res = await processMaterial(materialId)
        setExtract(res.text_extract || '')
      } catch (e: any) {
        // Non-fatal; user can paste text
      } finally {
        setLoadingExtract(false)
      }
    }
    load()
  }, [materialId])

  return (
    <Card>
      <CardHeader><CardTitle>AI Tools</CardTitle></CardHeader>
      <CardContent>
        <Accordion>
          <SummaryItem materialId={materialId} extract={extract} loadingExtract={loadingExtract} />
          <FlashcardsItem materialId={materialId} extract={extract} loadingExtract={loadingExtract} />
          <MCQItem materialId={materialId} extract={extract} loadingExtract={loadingExtract} />
          <ExplainItem materialId={materialId} extract={extract} loadingExtract={loadingExtract} />
        </Accordion>
      </CardContent>
    </Card>
  )
}

function CachedBadge({ createdAt }: { createdAt?: string }) {
  if (!createdAt) return null
  return (
    <span className="ml-2 inline-flex items-center gap-1 rounded-full border border-amber-300 bg-amber-50 px-2 py-0.5 text-[10px] text-amber-700 dark:bg-amber-900/20 dark:border-amber-800 dark:text-amber-300">
      <BadgeInfo size={12} /> Cached {humanTime(createdAt)}
    </span>
  )
}

function SummaryItem({ materialId, extract, loadingExtract }: { materialId: number; extract: string; loadingExtract: boolean }) {
  const tool: AITool = 'summary'
  const cached = loadCache<string>(materialId, tool)
  const [text, setText] = useState<string>('')
  const [out, setOut] = useState<string>(cached?.content || '')
  const [loading, setLoading] = useState(false)
  const [unsaved, setUnsaved] = useState(false)
  useEffect(() => { if (!text && extract) setText(extract) }, [extract])
  async function run(generateFresh = false) {
    setLoading(true)
    try {
      const res = await summarize(text)
      setOut(res.summary)
      setUnsaved(true)
      if (generateFresh) toast.success('Regenerated summary')
      else toast.success('Summary generated')
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to summarize')
    } finally { setLoading(false) }
  }
  function onSave() { saveCache(materialId, tool, out, { params: { length: text?.length } }); setUnsaved(false); toast.success('Saved to cache') }
  function onClear() { clearCache(materialId, tool); setOut(''); setUnsaved(false); toast.success('Cleared') }
  return (
    <AccordionItem id="summary" title={<div>Summary {unsaved && <span className="ml-2 text-[10px] text-amber-600">Unsaved result</span>}</div>} badge={<CachedBadge createdAt={cached?.meta.createdAt} />} defaultOpen>
      {loadingExtract ? <Skeleton className="h-16 w-full" /> : <Textarea value={text} onChange={(e) => setText(e.target.value)} className="h-32" />}
      <div className="mt-2 flex gap-2">
        <Button onClick={() => run(false)} disabled={loading}>{loading ? 'Generating...' : 'Generate'}</Button>
        <ToolControls onRegenerate={() => run(true)} onSave={onSave} onClear={onClear} onRestoreCached={() => { if (cached?.content) setOut(cached.content) }} hasCached={!!cached} />
      </div>
      {out && <div className="mt-2 rounded-md border bg-slate-50 p-3 text-sm whitespace-pre-wrap dark:bg-slate-800 dark:border-slate-700"><Copy text={out} /> <div className="mt-1">{out}</div></div>}
    </AccordionItem>
  )
}

function FlashcardsItem({ materialId, extract, loadingExtract }: { materialId: number; extract: string; loadingExtract: boolean }) {
  const tool: AITool = 'flashcards'
  const cached = loadCache<{ question: string; answer: string }[]>(materialId, tool)
  const [text, setText] = useState<string>('')
  const [num, setNum] = useState<number>(5)
  const [cards, setCards] = useState<{ question: string; answer: string }[]>(cached?.content || [])
  const [loading, setLoading] = useState(false)
  const [unsaved, setUnsaved] = useState(false)
  useEffect(() => { if (!text && extract) setText(extract) }, [extract])
  async function run(generateFresh = false) {
    setLoading(true)
    try {
      const res = await generateFlashcards(text, num)
      setCards(res.flashcards)
      setUnsaved(true)
      toast.success(generateFresh ? 'Regenerated flashcards' : 'Flashcards generated')
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to generate flashcards')
    } finally { setLoading(false) }
  }
  function onSave() { saveCache(materialId, tool, cards, { params: { num } }); setUnsaved(false); toast.success('Saved to cache') }
  function onClear() { clearCache(materialId, tool); setCards([]); setUnsaved(false); toast.success('Cleared') }
  return (
    <AccordionItem id="flashcards" title={<div>Flashcards {unsaved && <span className="ml-2 text-[10px] text-amber-600">Unsaved result</span>}</div>} badge={<CachedBadge createdAt={cached?.meta.createdAt} />}>
      {loadingExtract ? <Skeleton className="h-16 w-full" /> : <Textarea value={text} onChange={(e) => setText(e.target.value)} className="h-32" />}
      <div className="mt-2 flex items-center gap-2 text-sm">
        Number of cards:
        <Input type="number" className="w-24" value={num} onChange={(e) => setNum(parseInt(e.target.value || '0'))} />
      </div>
      <div className="mt-2 flex gap-2">
        <Button onClick={() => run(false)} disabled={loading}>{loading ? 'Generating...' : 'Generate'}</Button>
        <ToolControls onRegenerate={() => run(true)} onSave={onSave} onClear={onClear} onRestoreCached={() => { if (cached?.content) setCards(cached.content) }} hasCached={!!cached} />
      </div>
      {!!cards.length && (
        <div className="mt-2 space-y-2">
          {cards.map((c, i) => (
            <div key={i} className="rounded-md border bg-white p-2 text-sm dark:bg-slate-900 dark:border-slate-700">
              <div className="font-medium">Q: {c.question}</div>
              <div>A: {c.answer}</div>
            </div>
          ))}
        </div>
      )}
    </AccordionItem>
  )
}

function MCQItem({ materialId, extract, loadingExtract }: { materialId: number; extract: string; loadingExtract: boolean }) {
  const tool: AITool = 'mcq'
  const cached = loadCache<any[]>(materialId, tool)
  const [text, setText] = useState<string>('')
  const [num, setNum] = useState<number>(5)
  const [qs, setQs] = useState<any[]>(cached?.content || [])
  const [loading, setLoading] = useState(false)
  const [unsaved, setUnsaved] = useState(false)
  useEffect(() => { if (!text && extract) setText(extract) }, [extract])
  async function run(generateFresh = false) {
    setLoading(true)
    try {
      const res = await generateMCQ(text, num)
      setQs(res.questions)
      setUnsaved(true)
      toast.success(generateFresh ? 'Regenerated MCQs' : 'MCQs generated')
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to generate MCQs')
    } finally { setLoading(false) }
  }
  function onSave() { saveCache(materialId, tool, qs, { params: { num } }); setUnsaved(false); toast.success('Saved to cache') }
  function onClear() { clearCache(materialId, tool); setQs([]); setUnsaved(false); toast.success('Cleared') }
  return (
    <AccordionItem id="mcq" title={<div>MCQ Generator {unsaved && <span className="ml-2 text-[10px] text-amber-600">Unsaved result</span>}</div>} badge={<CachedBadge createdAt={cached?.meta.createdAt} />}>
      {loadingExtract ? <Skeleton className="h-16 w-full" /> : <Textarea value={text} onChange={(e) => setText(e.target.value)} className="h-32" />}
      <div className="mt-2 flex items-center gap-2 text-sm">
        Number of questions:
        <Input type="number" className="w-24" value={num} onChange={(e) => setNum(parseInt(e.target.value || '0'))} />
      </div>
      <div className="mt-2 flex gap-2">
        <Button onClick={() => run(false)} disabled={loading}>{loading ? 'Generating...' : 'Generate'}</Button>
        <ToolControls onRegenerate={() => run(true)} onSave={onSave} onClear={onClear} onRestoreCached={() => { if (cached?.content) setQs(cached.content) }} hasCached={!!cached} />
      </div>
      {!!qs.length && (
        <div className="mt-2 space-y-3">
          {qs.map((q, i) => (
            <div key={i} className="rounded-md border bg-white p-2 text-sm dark:bg-slate-900 dark:border-slate-700">
              <div className="font-medium">{q.question}</div>
              <ul className="mt-1 ml-4 list-disc">
                {q.options?.map((o: any, j: number) => (
                  <li key={j} className={o.is_correct ? 'text-green-700' : ''}>{o.text}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </AccordionItem>
  )
}

function ExplainItem({ materialId, extract, loadingExtract }: { materialId: number; extract: string; loadingExtract: boolean }) {
  const tool: AITool = 'explain'
  const cached = loadCache<string>(materialId, tool)
  const [concept, setConcept] = useState<string>('')
  const [context, setContext] = useState<string>('')
  const [out, setOut] = useState<string>(cached?.content || '')
  const [loading, setLoading] = useState(false)
  const [unsaved, setUnsaved] = useState(false)
  useEffect(() => { if (!context && extract) setContext(extract.slice(0, 2000)) }, [extract])
  async function run(generateFresh = false) {
    setLoading(true)
    try {
      const res = await explain(concept, context)
      setOut(res.explanation)
      setUnsaved(true)
      toast.success(generateFresh ? 'Regenerated explanation' : 'Explanation generated')
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || 'Failed to explain')
    } finally { setLoading(false) }
  }
  function onSave() { saveCache(materialId, tool, out, { params: { conceptLen: concept.length } }); setUnsaved(false); toast.success('Saved to cache') }
  function onClear() { clearCache(materialId, tool); setOut(''); setUnsaved(false); toast.success('Cleared') }
  return (
    <AccordionItem id="explain" title={<div>Concept Explanation {unsaved && <span className="ml-2 text-[10px] text-amber-600">Unsaved result</span>}</div>} badge={<CachedBadge createdAt={cached?.meta.createdAt} />}>
      <Input placeholder="Concept (e.g., Newton's Second Law)" value={concept} onChange={(e) => setConcept(e.target.value)} />
      {loadingExtract ? <Skeleton className="h-16 w-full" /> : <Textarea placeholder="Optional context" value={context} onChange={(e) => setContext(e.target.value)} className="h-28" />}
      <div className="mt-2 flex gap-2">
        <Button onClick={() => run(false)} disabled={loading}>{loading ? 'Generating...' : 'Generate'}</Button>
        <ToolControls onRegenerate={() => run(true)} onSave={onSave} onClear={onClear} onRestoreCached={() => { if (cached?.content) setOut(cached.content) }} hasCached={!!cached} />
      </div>
      {out && <div className="mt-2 rounded-md border bg-slate-50 p-3 text-sm whitespace-pre-wrap dark:bg-slate-800 dark:border-slate-700"><Copy text={out} /> <div className="mt-1">{out}</div></div>}
    </AccordionItem>
  )
}
