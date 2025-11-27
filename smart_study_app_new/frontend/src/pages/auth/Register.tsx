import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select } from '@/components/ui/select'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { register as apiRegister } from '@/lib/api'

export default function Register() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [fullName, setFullName] = useState('')
  const [role, setRole] = useState('student')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    try {
      await apiRegister({ email, full_name: fullName, password, role: role as any })
      navigate('/login')
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Registration failed')
    }
  }

  return (
    <div className="grid min-h-screen place-items-center bg-gradient">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Create Account</CardTitle>
        </CardHeader>
        <CardContent>
          <form className="space-y-3" onSubmit={onSubmit}>
            {error && <div className="rounded-md border border-red-300 bg-red-50 p-2 text-sm text-red-700">{error}</div>}
            <div>
              <label className="mb-1 block text-sm font-medium">Full Name</label>
              <Input value={fullName} onChange={(e) => setFullName(e.target.value)} />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Email</label>
              <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Role</label>
              <Select value={role} onChange={setRole}>
                <option value="student">Student</option>
                <option value="teacher">Teacher</option>
                <option value="admin">Admin</option>
              </Select>
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">Password</label>
              <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </div>
            <Button type="submit" className="w-full">Register</Button>
            <div className="text-center text-sm">
              Have an account? <Link to="/login" className="text-blue-600 hover:underline">Login</Link>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
