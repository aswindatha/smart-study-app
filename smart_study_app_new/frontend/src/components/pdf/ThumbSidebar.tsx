import { Document, Page } from 'react-pdf'

export default function ThumbSidebar({ url, numPages, currentPage, onSelect }: {
  url: string
  numPages: number
  currentPage: number
  onSelect: (n: number) => void
}) {
  const thumbs = [] as JSX.Element[]
  for (let i = 1; i <= numPages; i++) {
    const isCurrent = i === currentPage
    const near = Math.abs(i - currentPage) <= 5
    thumbs.push(
      <button key={i} onClick={() => onSelect(i)} className={`block w-full px-1 py-2 text-left ${isCurrent ? 'bg-blue-50 dark:bg-blue-900/30' : 'hover:bg-slate-50 dark:hover:bg-slate-800'}`}>
        {near ? (
          <div className={`rounded-md border ${isCurrent ? 'border-blue-400 dark:border-blue-600' : 'border-slate-200 dark:border-slate-700'}`}>
            <Document file={url}>
              <Page pageNumber={i} width={90} renderAnnotationLayer={false} renderTextLayer={false} />
            </Document>
          </div>
        ) : (
          <div className="h-[120px] w-full rounded-md border border-dashed border-slate-200 text-center text-[10px] text-slate-400">Page {i}</div>
        )}
      </button>
    )
  }
  return <div className="p-1">{thumbs}</div>
}
