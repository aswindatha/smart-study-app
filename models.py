from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Student Models
class StudentBase(BaseModel):
    user_id: Optional[int] = None
    name: str
    current_course_id: Optional[int] = None
    progress: float = 0.0
    cognitive_limit: int = 50
    emotional_state: str = "neutral"

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    id: int
    
    class Config:
        from_attributes = True

# Course Models
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    video_url: Optional[str] = None
    pdf_url: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class Course(CourseBase):
    id: int
    
    class Config:
        from_attributes = True

# Note Models
class NoteBase(BaseModel):
    student_id: int
    file_path: str
    summary: Optional[str] = None

class NoteCreate(NoteBase):
    pass

class Note(NoteBase):
    id: int
    
    class Config:
        from_attributes = True

# Dashboard Response Model
class DashboardResponse(BaseModel):
    student: Student
    current_course: Optional[Course] = None
    progress_percentage: float
    emotional_state: str
    cognitive_load_level: str
    recommended_next_course: Optional[Course] = None

# Progress Update Request
class ProgressUpdate(BaseModel):
    time_spent: float
    gaze_score: float  # 0 to 1
    face_attention_score: float  # 0 to 1

# Progress Response
class ProgressResponse(BaseModel):
    new_progress: float
    cognitive_load: float
    engagement_level: float
    emotional_state: str

# Chatbot Request/Response
class ChatbotRequest(BaseModel):
    message: str
    context: Optional[str] = None

class ChatbotResponse(BaseModel):
    response: str
    type: str  # summarize, explain, key_points

# Image Analysis Request/Response
class ImageAnalysisRequest(BaseModel):
    image_data: str  # Base64 encoded image
    student_id: int

class ImageAnalysisResponse(BaseModel):
    gaze_score: float
    face_attention_score: float
    emotional_state: str
    face_detected: bool
    cognitive_load: float
    engagement_level: float

# Teacher Models
class TeacherStudentInfo(BaseModel):
    id: int
    name: str
    current_course_id: Optional[int] = None
    progress: float
    emotional_state: str
    cognitive_limit: int
    current_course_title: Optional[str] = None
    
    class Config:
        from_attributes = True

class StudentLimitsUpdate(BaseModel):
    cognitive_limit: int
    assigned_course_id: Optional[int] = None

class MetricsHistory(BaseModel):
    id: int
    student_id: int
    timestamp: str
    gaze_score: float
    face_attention: float
    cognitive_load: float
    emotional_state: str
    progress: float
    
    class Config:
        from_attributes = True

class StudentAnalytics(BaseModel):
    student_id: int
    student_name: str
    progress_history: list[MetricsHistory]
    cognitive_load_history: list[float]
    emotional_state_distribution: dict[str, int]
    engagement_scores: list[float]
    average_cognitive_load: float
    average_engagement: float
    total_sessions: int

# Authentication Models
class UserRegister(BaseModel):
    name: str
    email: str
    password: str
    role: str  # "student" or "teacher"

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: str
    
    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    status: str
    role: str
    user_id: int
    user_name: str
    student_id: Optional[int] = None
    teacher_id: Optional[int] = None

# Teacher Models
class TeacherBase(BaseModel):
    user_id: int
    department: Optional[str] = None
    specialization: Optional[str] = None
    experience_years: int = 0

class TeacherCreate(TeacherBase):
    pass

class Teacher(TeacherBase):
    id: int
    
    class Config:
        from_attributes = True
