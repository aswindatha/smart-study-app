import { useSessionStore } from '@/store/session'
import { useElapsed } from '@/hooks/useElapsed'
import { Button } from '@/components/ui/button'
import { motion, AnimatePresence } from 'framer-motion'

export default function FloatingTimer() {
  const active = useSessionStore((s) => s.activeSession)
  const end = useSessionStore((s) => s.endSession)
  const { label } = useElapsed(active?.start_time || null)

  return (
    <AnimatePresence>
      {active && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 12 }}
          transition={{ duration: 0.2 }}
          className="fixed bottom-4 right-4 z-40 rounded-lg border border-slate-200 bg-white/90 p-3 shadow-lg backdrop-blur dark:border-slate-800 dark:bg-slate-900/80"
        >
          <div className="flex items-center gap-3">
            <div className="text-sm font-medium">Session: {label}</div>
            <Button size="sm" variant="secondary" onClick={() => end()}>End</Button>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  )
}
