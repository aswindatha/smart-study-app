import { useEffect, useState, useCallback } from 'react'
import 'react-pdf/dist/Page/AnnotationLayer.css'
import 'react-pdf/dist/Page/TextLayer.css'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ZoomIn, ZoomOut, ChevronLeft, ChevronRight, FileText, LocateFixed } from 'lucide-react'
import ThumbSidebar from '@/components/pdf/ThumbSidebar'
import GoToPageDialog from '@/components/ui/GoToPageDialog'
import { motion, AnimatePresence } from 'framer-motion'

type PDFMod = typeof import('react-pdf')

export default function PDFViewer({ url }: { url: string }) {
  const [numPages, setNumPages] = useState<number>(0)
  const [pageNumber, setPageNumber] = useState<number>(1)
  const [scale, setScale] = useState<number>(1.2)
  const [gotoOpen, setGotoOpen] = useState(false)
  const [pdf, setPdf] = useState<PDFMod | null>(null)

  useEffect(() => {
    let mounted = true
    import('react-pdf').then((mod) => {
      if (!mounted) return
      // Configure worker
      mod.pdfjs.GlobalWorkerOptions.workerSrc = new URL('pdfjs-dist/build/pdf.worker.min.mjs', import.meta.url).toString()
      setPdf(mod)
    })
    return () => { mounted = false }
  }, [])

  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages)
    setPageNumber(1)
  }

  const goPrev = useCallback(() => setPageNumber((p) => Math.max(1, p - 1)), [])
  const goNext = useCallback(() => setPageNumber((p) => Math.min(numPages, p + 1)), [numPages])
  const zoomIn = useCallback(() => setScale((s) => Math.min(3, s + 0.2)), [])
  const zoomOut = useCallback(() => setScale((s) => Math.max(0.6, s - 0.2)), [])

  const controls = (
    <div className="flex items-center gap-2">
      <Button variant="outline" onClick={() => setGotoOpen(true)} title="Go to page"><LocateFixed size={16} /></Button>
      <Button variant="outline" onClick={zoomOut}><ZoomOut size={16} /></Button>
      <div className="text-sm min-w-[70px] text-center">{Math.round(scale * 100)}%</div>
      <Button variant="outline" onClick={zoomIn}><ZoomIn size={16} /></Button>
      <div className="mx-2 h-6 w-px bg-slate-300" />
      <Button variant="outline" onClick={goPrev} disabled={pageNumber <= 1}><ChevronLeft size={16} /></Button>
      <div className="text-sm">Page {pageNumber} / {numPages || '-'}</div>
      <Button variant="outline" onClick={goNext} disabled={pageNumber >= numPages}><ChevronRight size={16} /></Button>
    </div>
  )

  return (
    <Card className="h-[80vh]">
      <CardHeader className="flex flex-row items-center justify-between">
        <div className="flex items-center gap-2"><FileText size={18} /><CardTitle>Document</CardTitle></div>
        {controls}
      </CardHeader>
      <CardContent className="h-[calc(80vh-84px)] overflow-hidden">
        <div className="flex h-full gap-3">
          <div className="w-28 shrink-0 overflow-auto border-r border-slate-200 dark:border-slate-800">
            {pdf && numPages > 0 && (
              <ThumbSidebar url={url} numPages={numPages} currentPage={pageNumber} onSelect={setPageNumber} />
            )}
          </div>
          <div className="flex-1 overflow-auto">
            {pdf ? (
              <pdf.Document file={url} onLoadSuccess={onDocumentLoadSuccess} loading={<div className="p-6 text-slate-500">Loading PDF...</div>}>
                <AnimatePresence mode="wait">
                  <motion.div key={`${pageNumber}-${scale}`}
                    initial={{ opacity: 0, y: 8, scale: 0.98 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -8, scale: 0.98 }}
                    transition={{ duration: 0.2 }}
                    className="flex justify-center"
                  >
                    <pdf.Page pageNumber={pageNumber} scale={scale} renderAnnotationLayer renderTextLayer />
                  </motion.div>
                </AnimatePresence>
              </pdf.Document>
            ) : (
              <div className="p-6 text-slate-500">Loading PDF...</div>
            )}
          </div>
        </div>
      </CardContent>
      <GoToPageDialog open={gotoOpen} onClose={() => setGotoOpen(false)} numPages={numPages} onGo={(n) => { setPageNumber(n); setGotoOpen(false) }} />
    </Card>
  )
}
