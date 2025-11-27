import { useEffect, useState } from 'react'
import { useAuthStore } from '@/store/auth'
import { api } from '@/lib/api'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function Profile() {
  const user = useAuthStore((s) => s.user)
  const setUser = useAuthStore((s) => (u: any) => s.user)
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [password, setPassword] = useState('')
  const [status, setStatus] = useState<string>('')

  useEffect(() => {
    if (user) {
      setEmail(user.email)
      setFullName(user.full_name || '')
    }
  }, [user])

  async function onSave(e: React.FormEvent) {
    e.preventDefault()
    if (!user) return
    const payload: any = { email, full_name: fullName }
    if (password) payload.password = password
    const { data } = await api.put(`/api/users/${user.id}`, payload)
    setStatus('Saved!')
  }

  return (
    <Card className="max-w-xl">
      <CardHeader><CardTitle>Profile</CardTitle></CardHeader>
      <CardContent>
        <form className="space-y-3" onSubmit={onSave}>
          <div>
            <label className="mb-1 block text-sm font-medium">Full Name</label>
            <Input value={fullName} onChange={(e) => setFullName(e.target.value)} />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">Email</label>
            <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <div>
            <label className="mb-1 block text-sm font-medium">New Password</label>
            <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          </div>
          <Button type="submit">Save</Button>
          {status && <div className="text-sm text-green-700">{status}</div>}
        </form>
      </CardContent>
    </Card>
  )
}
