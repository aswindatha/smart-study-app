export default function Skeleton({ className = '' }: { className?: string }) {
  return (
    <div
      className={`animate-shimmer bg-gradient-to-r from-slate-100 via-slate-200 to-slate-100 bg-[length:1000px_100%] ${className} rounded-md`}
    />
  )
}
