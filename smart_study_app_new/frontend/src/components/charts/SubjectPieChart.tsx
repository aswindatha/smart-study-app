import { Doughnut } from 'react-chartjs-2'

export default function SubjectPieChart({ bySubject }: { bySubject: { subject: string; minutes?: number; total_minutes?: number }[] }) {
  const labels = bySubject.map((s) => s.subject || 'Unknown')
  const values = bySubject.map((s) => s.minutes ?? s.total_minutes ?? 0)
  const data = {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor: ['#60a5fa','#34d399','#fbbf24','#f472b6','#a78bfa','#f87171','#22d3ee','#facc15'],
        borderWidth: 0,
      },
    ],
  }
  const options = {
    plugins: { legend: { position: 'right' as const }, tooltip: { callbacks: { label: (ctx: any) => `${ctx.label}: ${ctx.raw} min` } } },
    cutout: '60%',
  }
  return <Doughnut data={data} options={options} />
}
