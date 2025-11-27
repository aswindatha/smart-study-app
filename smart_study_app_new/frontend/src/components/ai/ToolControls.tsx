import { Button } from '@/components/ui/button'

export default function ToolControls({
  onRegenerate,
  onSave,
  onClear,
  onRestoreCached,
  hasCached,
}: {
  onRegenerate: () => void
  onSave: () => void
  onClear: () => void
  onRestoreCached: () => void
  hasCached: boolean
}) {
  return (
    <div className="flex items-center gap-2">
      <Button variant="secondary" type="button" onClick={onRegenerate}>Regenerate</Button>
      <Button variant="outline" type="button" onClick={onSave}>Save</Button>
      <Button variant="outline" type="button" onClick={onClear}>Clear</Button>
      {hasCached && (
        <button type="button" className="text-xs text-blue-600 hover:underline" onClick={onRestoreCached}>
          Restore from cache
        </button>
      )}
    </div>
  )
}
