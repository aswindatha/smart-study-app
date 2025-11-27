from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# User Schemas
class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole = UserRole.STUDENT

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Study Material Schemas
class StudyMaterialBase(BaseModel):
    title: str
    description: Optional[str] = None
    subject: Optional[str] = None
    tags: Optional[str] = None

class StudyMaterialCreate(StudyMaterialBase):
    pass

class StudyMaterialUpdate(StudyMaterialBase):
    title: Optional[str] = None

class StudyMaterial(StudyMaterialBase):
    id: int
    owner_id: int
    file_path: str
    created_at: datetime

    class Config:
        from_attributes = True

# Study Session Schemas
class StudySessionBase(BaseModel):
    material_id: int
    duration_minutes: int

class StudySessionCreate(StudySessionBase):
    pass

class StudySession(StudySessionBase):
    id: int
    user_id: int
    start_time: datetime
    end_time: Optional[datetime] = None

    class Config:
        from_attributes = True

# AI Processing Schemas
class AISummaryRequest(BaseModel):
    text: str
    max_length: int = 300

class AISummaryResponse(BaseModel):
    summary: str

class AIGenerateFlashcardsRequest(BaseModel):
    text: str
    num_cards: int = 5

class Flashcard(BaseModel):
    question: str
    answer: str

class AIGenerateFlashcardsResponse(BaseModel):
    flashcards: List[Flashcard]

class AIGenerateMCQRequest(BaseModel):
    text: str
    num_questions: int = 5

class MCQOption(BaseModel):
    text: str
    is_correct: bool

class MCQQuestion(BaseModel):
    question: str
    options: List[MCQOption]

class AIGenerateMCQResponse(BaseModel):
    questions: List[MCQQuestion]

class AIExplainRequest(BaseModel):
    concept: str
    context: Optional[str] = None

class AIExplainResponse(BaseModel):
    explanation: str

# Analytics Schemas
class StudyAnalytics(BaseModel):
    total_study_time: int  # in minutes
    materials_studied: int
    average_score: Optional[float] = None
    last_studied: Optional[datetime] = None

class MaterialAnalytics(BaseModel):
    material_id: int
    title: str
    study_sessions: int
    total_time: int  # in minutes
    last_studied: Optional[datetime] = None

class UserAnalyticsResponse(BaseModel):
    user_id: int
    overall: StudyAnalytics
    by_subject: dict[str, StudyAnalytics]
    recent_materials: List[MaterialAnalytics]
