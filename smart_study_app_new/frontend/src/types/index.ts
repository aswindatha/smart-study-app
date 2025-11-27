export type Role = 'student' | 'teacher' | 'admin'

export interface User {
  id: number
  email: string
  full_name?: string
  role: Role
  is_active: boolean
  created_at: string
}

export interface StudyMaterial {
  id: number
  title: string
  description?: string
  file_path: string
  subject?: string
  tags?: string
  owner_id: number
  created_at: string
}

export interface StudySession {
  id: number
  user_id: number
  material_id: number
  start_time: string
  end_time?: string | null
  duration_minutes: number
}
