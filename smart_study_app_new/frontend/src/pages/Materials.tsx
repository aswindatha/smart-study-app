import { useEffect, useState } from 'react'
import { listMaterials, uploadMaterial, deleteMaterial } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import Skeleton from '@/components/ui/skeleton'
import type { StudyMaterial } from '@/types'

export default function Materials() {
  const [materials, setMaterials] = useState<StudyMaterial[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [form, setForm] = useState({ title: '', description: '', subject: '', tags: '' })
  const [file, setFile] = useState<File | null>(null)

  async function load() {
    setLoading(true)
    const data = await listMaterials()
    setMaterials(data)
    setLoading(false)
  }

  useEffect(() => { load() }, [])

  async function onUpload(e: React.FormEvent) {
    e.preventDefault()
    if (!file) return
    setUploading(true)
    await uploadMaterial({ ...form, file })
    setForm({ title: '', description: '', subject: '', tags: '' })
    setFile(null)
    setUploading(false)
    await load()
  }

  async function onDelete(id: number) {
    await deleteMaterial(id)
    await load()
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader><CardTitle>Upload Material</CardTitle></CardHeader>
        <CardContent>
          <form className="grid gap-3 sm:grid-cols-2" onSubmit={onUpload}>
            <div>
              <label className="mb-1 block text-sm font-medium">Title</label>
              <Input value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} required />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Subject</label>
              <Input value={form.subject} onChange={(e) => setForm((f) => ({ ...f, subject: e.target.value }))} />
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium">Description</label>
              <Textarea value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} />
            </div>
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium">Tags (comma-separated)</label>
              <Input value={form.tags} onChange={(e) => setForm((f) => ({ ...f, tags: e.target.value }))} />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">File (PDF or TXT)</label>
              <Input type="file" accept=".pdf,.txt" onChange={(e) => setFile(e.target.files?.[0] || null)} required />
            </div>
            <div className="flex items-end">
              <Button type="submit" disabled={uploading}>{uploading ? 'Uploading...' : 'Upload'}</Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle>My Materials</CardTitle></CardHeader>
        <CardContent>
          {loading ? (
            <Skeleton className="h-40 w-full" />
          ) : (
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b">
                  <th className="py-2">Title</th>
                  <th className="py-2">Subject</th>
                  <th className="py-2">Tags</th>
                  <th className="py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {materials.map((m) => (
                  <tr key={m.id} className="border-b">
                    <td className="py-2 font-medium">{m.title}</td>
                    <td className="py-2">{m.subject || '-'}</td>
                    <td className="py-2">{m.tags || '-'}</td>
                    <td className="py-2 flex gap-2">
                      <a className="text-blue-600 hover:underline" href={`/materials/${m.id}`}>Open</a>
                      <button className="text-red-600 hover:underline" onClick={() => onDelete(m.id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
