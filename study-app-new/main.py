from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import List, Optional
import os
import uuid
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    init_database()
    migrate_database()
    yield

app = FastAPI(title="Smart Learning App", version="1.0.0", lifespan=lifespan)

# Initialize Gemini API
# TODO: Replace this placeholder with your actual Gemini API key
API_KEY = "AIzaSyC_J6WNngG4oxK2b_eagK3_TR7-0tv4IH4"
genai.configure(api_key=API_KEY)

# Mount static files
app.mount("/frontend", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "frontend")), name="frontend")

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "uploads")), name="uploads")

# Add imports after app creation
from database import get_db, init_database, migrate_database
from models import (
    Student, Course, Note, DashboardResponse, 
    ProgressUpdate, ProgressResponse, ChatbotRequest, ChatbotResponse,
    ImageAnalysisRequest, ImageAnalysisResponse,
    TeacherStudentInfo, StudentLimitsUpdate, MetricsHistory, StudentAnalytics,
    CourseCreate, StudentCreate,
    UserRegister, UserLogin, UserResponse, LoginResponse,
    TeacherCreate, Teacher
)
from utils import (
    calculate_cognitive_load, calculate_engagement, 
    simple_text_summarizer, extract_text_from_pdf, extract_text_from_txt,
    get_cognitive_load_level, get_recommended_next_course,
    analyze_face_from_image, detect_emotional_state
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper functions
def get_student_by_id(student_id: int):
    """Get student by ID or raise 404"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        student_data = cursor.fetchone()
        if not student_data:
            raise HTTPException(status_code=404, detail="Student not found")
        return Student(**student_data)

def get_course_by_id(course_id: int):
    """Get course by ID or raise 404"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
        course_data = cursor.fetchone()
        if not course_data:
            raise HTTPException(status_code=404, detail="Course not found")
        return Course(**course_data)

def get_all_courses():
    """Get all courses"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM courses ORDER BY id")
        courses_data = cursor.fetchall()
        return [Course(**course) for course in courses_data]

# ENDPOINTS

@app.get("/")
async def root():
    return {"message": "Smart Learning App API"}

@app.get("/students/{student_id}/dashboard", response_model=DashboardResponse)
async def get_student_dashboard(student_id: int):
    """Get student dashboard with current course, progress, and recommendations"""
    student = get_student_by_id(student_id)
    
    # Get current course if any
    current_course = None
    if student.current_course_id:
        current_course = get_course_by_id(student.current_course_id)
    
    # Get recommended next course
    recommended_course = None
    if student.current_course_id:
        next_course_id = get_recommended_next_course(student_id, student.current_course_id)
        try:
            recommended_course = get_course_by_id(next_course_id)
        except HTTPException:
            # No next course available
            pass
    else:
        # If no current course, recommend first course
        all_courses = get_all_courses()
        if all_courses:
            recommended_course = all_courses[0]
    
    # Calculate cognitive load level
    cognitive_load_level = get_cognitive_load_level(50)  # Default, would be calculated from actual data
    
    return DashboardResponse(
        student=student,
        current_course=current_course,
        progress_percentage=student.progress * 100,
        emotional_state=student.emotional_state,
        cognitive_load_level=cognitive_load_level,
        recommended_next_course=recommended_course
    )

@app.get("/courses", response_model=List[Course])
async def get_courses():
    """List all available courses"""
    return get_all_courses()

@app.get("/courses/{course_id}", response_model=Course)
async def get_course(course_id: int):
    """Get individual course details"""
    course = get_course_by_id(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@app.post("/students/{student_id}/start_course/{course_id}")
async def start_course(student_id: int, course_id: int):
    """Assign a course to the student and reset progress"""
    student = get_student_by_id(student_id)
    course = get_course_by_id(course_id)
    
    with get_db() as conn:
        cursor = conn.cursor()
        # Update student's current course and reset progress
        cursor.execute(
            "UPDATE students SET current_course_id = ?, progress = 0.0, emotional_state = 'neutral' WHERE id = ?",
            (course_id, student_id)
        )
        conn.commit()
    
    return {"message": f"Student {student_id} started course '{course.title}'", "course_id": course_id}

@app.post("/students/{student_id}/update_progress", response_model=ProgressResponse)
async def update_student_progress(student_id: int, progress_data: ProgressUpdate):
    """Update student progress based on time spent, gaze score, and face attention"""
    student = get_student_by_id(student_id)
    
    # Get current course ID from student or from request
    current_course_id = student.current_course_id
    if not current_course_id:
        # Try to get course ID from progress data if available
        current_course_id = getattr(progress_data, 'course_id', None)
    
    if not current_course_id:
        raise HTTPException(status_code=400, detail="No active course found")
    
    # Calculate cognitive metrics
    cognitive_load, emotional_state = calculate_cognitive_load(
        progress_data.gaze_score, student.cognitive_limit
    )
    engagement_level = calculate_engagement(progress_data.face_attention_score)
    
    # Get current course progress from student_courses table
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT progress, total_time_spent FROM student_courses WHERE student_id = ? AND course_id = ?",
            (student_id, current_course_id)
        )
        course_progress_data = cursor.fetchone()
        
        if not course_progress_data:
            # Create enrollment if not exists
            cursor.execute(
                "INSERT INTO student_courses (student_id, course_id, progress, total_time_spent) VALUES (?, ?, ?, ?)",
                (student_id, current_course_id, 0.0, 0.0)
            )
            current_course_progress = 0.0
            current_time_spent = 0.0
        else:
            current_course_progress, current_time_spent = course_progress_data
    
    # Calculate progress increase based on multiple factors
    # Base progress from time spent (1 minute = ~1% progress base)
    base_progress = progress_data.time_spent * 0.8  # More conservative progression
    
    # Engagement multiplier (0.5x to 1.5x based on engagement)
    engagement_multiplier = 0.5 + (engagement_level / 100) * 1.0
    
    # Cognitive load factor (too high or too low cognitive load reduces learning)
    if cognitive_load > 85:  # Overwhelmed
        cognitive_factor = 0.7
    elif cognitive_load > student.cognitive_limit:  # Stressed
        cognitive_factor = 0.8
    elif cognitive_load < 25:  # Bored/under-challenged
        cognitive_factor = 0.85
    else:  # Optimal range
        cognitive_factor = 1.0
    
    # Calculate final progress increase
    progress_increase = base_progress * engagement_multiplier * cognitive_factor
    new_course_progress = min(1.0, current_course_progress + progress_increase)  # Cap at 100%
    new_total_time_spent = current_time_spent + progress_data.time_spent
    
    # Debug logging
    print(f"Course-Specific Progress Update Debug:")
    print(f"  Student ID: {student_id}")
    print(f"  Course ID: {current_course_id}")
    print(f"  Gaze Score: {progress_data.gaze_score:.3f}")
    print(f"  Face Attention: {progress_data.face_attention_score:.3f}")
    print(f"  Time Spent: {progress_data.time_spent:.2f} min")
    print(f"  Student Limit: {student.cognitive_limit}")
    print(f"  Calculated Cognitive Load: {cognitive_load:.1f}%")
    print(f"  Emotional State: {emotional_state}")
    print(f"  Engagement Level: {engagement_level:.1f}%")
    print(f"  Current Course Progress: {current_course_progress:.3f}")
    print(f"  Progress Increase: {progress_increase:.3f}")
    print(f"  New Course Progress: {new_course_progress:.3f}")
    print(f"  Total Time Spent: {new_total_time_spent:.2f} min")
    
    # Update course-specific progress in database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE student_courses SET progress = ?, total_time_spent = ? WHERE student_id = ? AND course_id = ?",
            (new_course_progress, new_total_time_spent, student_id, current_course_id)
        )
        
        # Update student's overall progress (average of all courses)
        cursor.execute(
            "SELECT AVG(progress) as avg_progress FROM student_courses WHERE student_id = ?",
            (student_id,)
        )
        avg_progress = cursor.fetchone()['avg_progress'] or 0.0
        
        # Update student's current course and overall progress
        cursor.execute(
            "UPDATE students SET progress = ?, emotional_state = ?, current_course_id = ? WHERE id = ?",
            (avg_progress, emotional_state, current_course_id, student_id)
        )
        
        # Save to metrics history for analytics
        cursor.execute(
            """INSERT INTO metrics_history 
               (student_id, gaze_score, face_attention, cognitive_load, emotional_state, progress)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (student_id, progress_data.gaze_score, progress_data.face_attention_score, 
             cognitive_load, emotional_state, new_course_progress)
        )
        
        conn.commit()
    
    return ProgressResponse(
        new_progress=new_course_progress,  # Return course-specific progress
        cognitive_load=cognitive_load,
        engagement_level=engagement_level,
        emotional_state=emotional_state
    )

@app.get("/students/{student_id}/courses/{course_id}/progress")
async def get_course_progress(student_id: int, course_id: int):
    """Get student's progress for a specific course"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT progress, total_time_spent FROM student_courses WHERE student_id = ? AND course_id = ?",
            (student_id, course_id)
        )
        course_data = cursor.fetchone()
        
        if not course_data:
            # Create enrollment if not exists
            cursor.execute(
                "INSERT INTO student_courses (student_id, course_id, progress, total_time_spent) VALUES (?, ?, ?, ?)",
                (student_id, course_id, 0.0, 0.0)
            )
            conn.commit()
            return {
                "progress_percentage": 0.0,
                "time_spent_minutes": 0.0,
                "course_completed": False
            }
        
        progress, time_spent = course_data
        return {
            "progress_percentage": progress * 100,
            "time_spent_minutes": time_spent,
            "course_completed": progress >= 1.0
        }

@app.get("/students/{student_id}/courses_with_progress")
async def get_student_courses_with_progress(student_id: int):
    """Get all courses with student's progress for each"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT c.id, c.title, c.description, c.video_url, c.pdf_url,
                   COALESCE(sc.progress, 0.0) as progress,
                   COALESCE(sc.total_time_spent, 0.0) as time_spent,
                   sc.status as enrollment_status
            FROM courses c
            LEFT JOIN student_courses sc ON c.id = sc.course_id AND sc.student_id = ?
            ORDER BY c.title
            """,
            (student_id,)
        )
        courses_data = cursor.fetchall()
        
        return [
            {
                "id": course["id"],
                "title": course["title"],
                "description": course["description"],
                "video_url": course["video_url"],
                "pdf_url": course["pdf_url"],
                "progress": course["progress"] * 100,
                "time_spent_minutes": course["time_spent"],
                "enrollment_status": course["enrollment_status"] or "not_enrolled"
            }
            for course in courses_data
        ]

@app.get("/students/{student_id}/metrics_history")
async def get_student_metrics_history(student_id: int, limit: int = 50):
    """Get student's metrics history"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM metrics_history 
               WHERE student_id = ? 
               ORDER BY timestamp DESC 
               LIMIT ?""",
            (student_id, limit)
        )
        
        metrics_data = cursor.fetchall()
        
        return [
            {
                "id": metric["id"],
                "timestamp": metric["timestamp"],
                "gaze_score": metric["gaze_score"],
                "face_attention": metric["face_attention"],
                "cognitive_load": metric["cognitive_load"],
                "emotional_state": metric["emotional_state"],
                "progress": metric["progress"],
                "engagement_level": calculate_engagement(metric["face_attention"])  # Calculate engagement from face attention
            }
            for metric in metrics_data
        ]

@app.post("/students/{student_id}/change_password")
async def change_student_password(student_id: int, password_data: dict):
    """Change student password"""
    try:
        current_password = password_data.get('current_password')
        new_password = password_data.get('new_password')
        
        if not current_password or not new_password:
            raise HTTPException(status_code=400, detail="Current password and new password are required")
        
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get current student data
            cursor.execute("SELECT password FROM students WHERE id = ?", (student_id,))
            student = cursor.fetchone()
            
            if not student:
                raise HTTPException(status_code=404, detail="Student not found")
            
            # Verify current password (in a real app, you'd use proper password hashing)
            if student['password'] != current_password:
                raise HTTPException(status_code=400, detail="Current password is incorrect")
            
            # Update password
            cursor.execute(
                "UPDATE students SET password = ? WHERE id = ?",
                (new_password, student_id)
            )
            conn.commit()
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error changing password: {str(e)}")

@app.post("/students/{student_id}/upload_notes")
async def upload_notes(student_id: int, file: UploadFile = File(...)):
    """Upload notes file (TXT/PDF) and store for viewing"""
    student = get_student_by_id(student_id)
    
    # Check file type
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ['.txt', '.pdf']:
        raise HTTPException(status_code=400, detail="Only TXT and PDF files are supported")
    
    # Read file content
    file_content = await file.read()
    
    # Extract text based on file type for storage
    if file_extension == '.pdf':
        extracted_text = extract_text_from_pdf(file_content)
    else:  # .txt
        extracted_text = extract_text_from_txt(file_content)
    
    # Save file to disk
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{uuid.uuid4()}_{file.filename}")
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Save note to database (use filename as title, no summary)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notes (student_id, file_path, summary) VALUES (?, ?, ?)",
            (student_id, file_path, file.filename)  # Use filename as summary for display
        )
        conn.commit()
    
    return {
        "message": "Notes uploaded successfully",
        "filename": file.filename,
        "file_path": file_path,
        "extracted_text_length": len(extracted_text)
    }

@app.post("/chatbot", response_model=ChatbotResponse)
async def chatbot_endpoint(
    message: str = Form(...),
    context: str = Form(""),
    student_id: int = Form(...),
    file: Optional[UploadFile] = File(None)
):
    """Enhanced chatbot with Gemini API and file upload support"""
    
    try:
        # Initialize variables
        full_context = context
        file_processed = False
        
        # Extract text from uploaded file if provided
        file_content = ""
        if file and file.filename:
            try:
                file_content = await extract_text_from_file(file)
                file_processed = True
                print(f"Extracted {len(file_content)} characters from {file.filename}")
            except Exception as e:
                print(f"Error processing file: {e}")
                return ChatbotResponse(
                    response="Error: Could not process the uploaded file. Please ensure it's a valid PDF or TXT file.",
                    type="error"
                )
        
        # Combine file content with context
        if file_content:
            if full_context:
                full_context += "\n\n" + file_content
            else:
                full_context = file_content
        
        # Initialize Gemini AI
        try:
            import google.generativeai as genai
            
            # Prepare prompt
            prompt = f"""
You are a helpful AI learning assistant. Answer the student's question based on the provided context.

Context: {full_context if full_context else "No specific context provided. Answer generally."}

Student Question: {message}

Provide a helpful, educational response:
"""
            
            # Configure API key from environment
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise Exception("GEMINI_API_KEY not found in environment variables")
            
            genai.configure(api_key=api_key)
            
            # Initialize model
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Generate response
            response = model.generate_content(prompt)
            ai_response = response.text
            
            if not ai_response:
                raise Exception("Empty response from Gemini")
                
        except Exception as e:
            print(f"Gemini API error: {e}")
            # Fallback to rule-based responses
            ai_response = get_fallback_response(message)
        
        return ChatbotResponse(
            response=ai_response,
            type="ai_response" if full_context else "general_response"
        )
        
    except Exception as e:
        print(f"Chatbot endpoint error: {e}")
        return ChatbotResponse(
            response="Sorry, I encountered an error. Please try again.",
            type="error"
        )

async def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from uploaded PDF or TXT file"""
    
    # Check file type
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ['.pdf', '.txt']:
        raise ValueError("Only PDF and TXT files are supported")
    
    # Read file content
    file_content = await file.read()
    
    if file_extension == '.pdf':
        # Extract text from PDF
        import PyPDF2
        import io
        
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from all pages
        extracted_text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text.strip():
                    extracted_text += f"\n--- Page {page_num + 1} ---\n"
                    extracted_text += page_text.strip() + "\n\n"
            except Exception as e:
                print(f"Error extracting text from page {page_num + 1}: {e}")
                continue
        
        return extracted_text.strip()
        
    elif file_extension == '.txt':
        # Read text file directly
        try:
            return file_content.decode('utf-8').strip()
        except UnicodeDecodeError:
            try:
                return file_content.decode('latin-1').strip()
            except UnicodeDecodeError:
                raise ValueError("Could not decode text file. Please ensure it's UTF-8 or Latin-1 encoded.")
    
def get_fallback_response(message: str) -> str:
    """Fallback rule-based responses when Gemini API fails"""
    
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['hello', 'hi', 'hey']):
        return "Hello! I'm your AI learning assistant. How can I help you today?"
    
    elif 'study' in message_lower:
        return "For effective studying, I recommend: 1) Take regular breaks using the Pomodoro Technique, 2) Use active recall by testing yourself, 3) Practice with exercises, 4) Get enough sleep for memory consolidation."
    
    elif 'python' in message_lower:
        return "Python is a versatile programming language! Key concepts include variables, data types, control flow (if/else, loops), functions, and object-oriented programming. Start with basic syntax and gradually move to more complex topics."
    
    elif 'math' in message_lower or 'mathematics' in message_lower:
        return "Mathematics builds step by step. Make sure you understand the fundamentals before moving to advanced topics. Practice regularly and don't hesitate to ask for help with specific concepts!"
    
    elif 'help' in message_lower:
        return "I'm here to help with your learning! You can: 1) Ask questions about your uploaded notes, 2) Upload PDF/TXT files for me to analyze, 3) Get general study advice, or 4) Request explanations on various topics."
    
    else:
        return "I'm here to help with your learning journey. Could you please provide more details about what you'd like to know? You can also upload notes or documents for more specific assistance."


def get_rule_based_response(message: str) -> str:
    """Fallback rule-based responses when Gemini API is unavailable"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['summarize', 'summary', 'sum up']):
        return "To get a summary, please upload your notes using the upload feature. I'll automatically extract and summarize the key points for you."
    elif any(word in message_lower for word in ['explain', 'explanation', 'understand', 'help']):
        return "I can help explain concepts. Please specify what topic you'd like me to explain, or refer to your course materials for detailed explanations."
    elif any(word in message_lower for word in ['key points', 'important', 'main points', 'highlights']):
        return "Key points are automatically extracted when you upload notes. The system identifies the most important sentences and concepts from your materials."
    elif any(word in message_lower for word in ['progress', 'how am i doing', 'performance']):
        return "Check your dashboard to see your current progress, cognitive load level, and emotional state. Your progress is updated based on your engagement and learning time."
    elif any(word in message_lower for word in ['course', 'next', 'recommend']):
        return "Check your dashboard for course recommendations. The system suggests the next course based on your current progress and learning patterns."
    else:
        return "I can help you with: summarizing notes, explaining concepts, identifying key points, checking progress, and course recommendations. Please be more specific about what you need."

@app.post("/analyze_image", response_model=ImageAnalysisResponse)
async def analyze_image_endpoint(request: ImageAnalysisRequest):
    """Analyze face image for gaze tracking and emotional state"""
    student = get_student_by_id(request.student_id)
    
    # Analyze face from image
    gaze_score, face_attention_score, face_detected = analyze_face_from_image(request.image_data)
    
    # Detect emotional state
    emotional_state = detect_emotional_state(request.image_data) if face_detected else "neutral"
    
    # Calculate cognitive load and engagement
    cognitive_load, _ = calculate_cognitive_load(gaze_score, student.cognitive_limit)
    engagement_level = calculate_engagement(face_attention_score)
    
    return ImageAnalysisResponse(
        gaze_score=gaze_score,
        face_attention_score=face_attention_score,
        emotional_state=emotional_state,
        face_detected=face_detected,
        cognitive_load=cognitive_load,
        engagement_level=engagement_level
    )

@app.get("/students/{student_id}/notes", response_model=List[Note])
async def get_student_notes(student_id: int):
    """Get all notes for a student"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notes WHERE student_id = ?", (student_id,))
        notes_data = cursor.fetchall()
        
        if not notes_data:
            return []
        
        return [Note(**note) for note in notes_data]

@app.get("/students/{student_id}/notes/{note_id}/content")
async def get_note_content(student_id: int, note_id: int):
    """Get the full content of a specific note"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM notes WHERE id = ? AND student_id = ?", (note_id, student_id))
            note_data = cursor.fetchone()
            
            if not note_data:
                raise HTTPException(status_code=404, detail="Note not found")
            
            file_path = note_data["file_path"]
            
            # Read file content
            if file_path.endswith('.pdf'):
                # For PDF, read file as bytes and extract text
                with open(file_path, 'rb') as f:
                    pdf_content = f.read()
                content = extract_text_from_pdf(pdf_content)
            else:
                # For text files
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            
            return {"content": content}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading note: {str(e)}")

@app.get("/students/{student_id}/notes/{note_id}/download")
async def download_note(student_id: int, note_id: int):
    """Download a note file"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT file_path FROM notes WHERE id = ? AND student_id = ?", (note_id, student_id))
            note_data = cursor.fetchone()
            
            if not note_data:
                raise HTTPException(status_code=404, detail="Note not found")
            
            file_path = note_data["file_path"]
            
            # Return file for download
            from fastapi.responses import FileResponse
            return FileResponse(
                path=file_path,
                filename=f"note_{note_id}.txt",
                media_type='text/plain'
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading note: {str(e)}")

@app.delete("/students/{student_id}/notes/{note_id}")
async def delete_student_note(student_id: int, note_id: int):
    """Delete a student's note"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get note file path for deletion
            cursor.execute("SELECT file_path FROM notes WHERE id = ? AND student_id = ?", (note_id, student_id))
            note = cursor.fetchone()
            
            if not note:
                raise HTTPException(status_code=404, detail="Note not found")
            
            # Delete file from filesystem
            file_path = note['file_path']
            if file_path:
                full_path = os.path.join(os.path.dirname(__file__), file_path.lstrip('/'))
                if os.path.exists(full_path):
                    os.remove(full_path)
            
            # Delete from database
            cursor.execute("DELETE FROM notes WHERE id = ? AND student_id = ?", (note_id, student_id))
            conn.commit()
            
            return {"message": "Note deleted successfully"}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting note: {str(e)}")

# TEACHER ENDPOINTS

@app.post("/teacher/courses/create", response_model=Course)
async def create_course_with_files(
    title: str = Form(...),
    description: str = Form(""),
    video_file: Optional[UploadFile] = File(None),
    pdf_file: Optional[UploadFile] = File(None)
):
    """Create a new course with file uploads"""
    import os
    import uuid
    from datetime import datetime
    
    # Create uploads directory if it doesn't exist
    uploads_dir = "uploads"
    os.makedirs(uploads_dir, exist_ok=True)
    
    video_url = None
    pdf_url = None
    
    # Handle video file upload
    if video_file:
        video_filename = f"{uuid.uuid4()}_{video_file.filename}"
        video_path = os.path.join(uploads_dir, video_filename)
        
        with open(video_path, "wb") as f:
            content = await video_file.read()
            f.write(content)
        
        video_url = f"/{uploads_dir}/{video_filename}"
    
    # Handle PDF file upload
    if pdf_file:
        pdf_filename = f"{uuid.uuid4()}_{pdf_file.filename}"
        pdf_path = os.path.join(uploads_dir, pdf_filename)
        
        with open(pdf_path, "wb") as f:
            content = await pdf_file.read()
            f.write(content)
        
        pdf_url = f"/{uploads_dir}/{pdf_filename}"
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO courses (title, description, video_url, pdf_url) VALUES (?, ?, ?, ?)",
            (title, description, video_url, pdf_url)
        )
        conn.commit()
        
        # Get the created course
        cursor.execute("SELECT * FROM courses WHERE id = last_insert_rowid()")
        course_data = cursor.fetchone()
        return Course(**course_data)

@app.put("/teacher/courses/{course_id}/edit", response_model=Course)
async def edit_course(
    course_id: int,
    title: str = Form(None),
    description: str = Form(None),
    video_file: Optional[UploadFile] = File(None),
    pdf_file: Optional[UploadFile] = File(None)
):
    """Edit an existing course with optional file uploads"""
    import os
    import uuid
    
    # Verify course exists
    course = get_course_by_id(course_id)
    
    # Get current course data
    current_title = course.title
    current_description = course.description
    current_video_url = course.video_url
    current_pdf_url = course.pdf_url
    
    # Update fields if provided
    new_title = title if title is not None else current_title
    new_description = description if description is not None else current_description
    new_video_url = current_video_url
    new_pdf_url = current_pdf_url
    
    # Handle video file upload
    if video_file:
        # Create uploads directory if it doesn't exist
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Save new video file
        video_filename = f"{uuid.uuid4()}_{video_file.filename}"
        video_path = os.path.join(uploads_dir, video_filename)
        
        with open(video_path, "wb") as f:
            content = await video_file.read()
            f.write(content)
        
        new_video_url = f"/{uploads_dir}/{video_filename}"
        
        # Delete old video file if it exists
        if current_video_url and current_video_url.startswith("/uploads/"):
            old_video_path = os.path.join(os.path.dirname(__file__), current_video_url.lstrip("/"))
            if os.path.exists(old_video_path):
                os.remove(old_video_path)
    
    # Handle PDF file upload
    if pdf_file:
        # Create uploads directory if it doesn't exist
        uploads_dir = "uploads"
        os.makedirs(uploads_dir, exist_ok=True)
        
        # Save new PDF file
        pdf_filename = f"{uuid.uuid4()}_{pdf_file.filename}"
        pdf_path = os.path.join(uploads_dir, pdf_filename)
        
        with open(pdf_path, "wb") as f:
            content = await pdf_file.read()
            f.write(content)
        
        new_pdf_url = f"/{uploads_dir}/{pdf_filename}"
        
        # Delete old PDF file if it exists
        if current_pdf_url and current_pdf_url.startswith("/uploads/"):
            old_pdf_path = os.path.join(os.path.dirname(__file__), current_pdf_url.lstrip("/"))
            if os.path.exists(old_pdf_path):
                os.remove(old_pdf_path)
    
    # Update course in database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE courses SET title = ?, description = ?, video_url = ?, pdf_url = ? WHERE id = ?",
            (new_title, new_description, new_video_url, new_pdf_url, course_id)
        )
        conn.commit()
        
        # Get updated course
        cursor.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
        course_data = cursor.fetchone()
        return Course(**course_data)

# Add missing course endpoints for frontend compatibility
@app.put("/courses/{course_id}", response_model=Course)
async def update_course(course_id: int, course: CourseCreate):
    """Update an existing course (alias for frontend compatibility)"""
    return await edit_course(course_id, course)

@app.delete("/courses/{course_id}")
async def delete_course(course_id: int):
    """Delete a course"""
    get_course_by_id(course_id)  # Verify course exists
    
    with get_db() as conn:
        cursor = conn.cursor()
        # Remove course from any students who have it assigned
        cursor.execute("UPDATE students SET current_course_id = NULL WHERE current_course_id = ?", (course_id,))
        # Delete the course
        cursor.execute("DELETE FROM courses WHERE id = ?", (course_id,))
        conn.commit()
    
    return {"message": f"Course {course_id} deleted successfully"}

@app.get("/teacher/students", response_model=List[TeacherStudentInfo])
async def get_all_students():
    """Get all students with their current course info"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, s.name, s.current_course_id, s.progress, s.emotional_state, s.cognitive_limit,
                   c.title as current_course_title
            FROM students s
            LEFT JOIN courses c ON s.current_course_id = c.id
            ORDER BY s.name
        """)
        students_data = cursor.fetchall()
        return [TeacherStudentInfo(**student) for student in students_data]

@app.put("/teacher/students/{student_id}")
async def update_student(student_id: int, student_data: dict):
    """Update student information"""
    get_student_by_id(student_id)  # Verify student exists
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Update only provided fields
        update_fields = []
        update_values = []
        
        if 'name' in student_data:
            update_fields.append("name = ?")
            update_values.append(student_data['name'])
        
        if 'email' in student_data:
            update_fields.append("email = ?")
            update_values.append(student_data['email'])
        
        if 'emotional_state' in student_data:
            update_fields.append("emotional_state = ?")
            update_values.append(student_data['emotional_state'])
        
        if 'cognitive_limit' in student_data:
            update_fields.append("cognitive_limit = ?")
            update_values.append(student_data['cognitive_limit'])
        
        if update_fields:
            update_values.append(student_id)
            cursor.execute(
                f"UPDATE students SET {', '.join(update_fields)} WHERE id = ?",
                tuple(update_values)
            )
            conn.commit()
    
    return {"message": f"Student {student_id} updated successfully"}

@app.delete("/teacher/students/{student_id}")
async def delete_student(student_id: int):
    """Delete a student"""
    get_student_by_id(student_id)  # Verify student exists
    
    with get_db() as conn:
        cursor = conn.cursor()
        # Delete student's notes first
        cursor.execute("DELETE FROM notes WHERE student_id = ?", (student_id,))
        # Delete the student
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
    
    return {"message": f"Student {student_id} deleted successfully"}

@app.put("/teacher/students/{student_id}/update_limits")
async def update_student_limits(student_id: int, limits: StudentLimitsUpdate):
    """Update student cognitive limit and assigned course"""
    get_student_by_id(student_id)  # Verify student exists
    
    # If course_id is provided, verify it exists
    if limits.assigned_course_id is not None:
        get_course_by_id(limits.assigned_course_id)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET cognitive_limit = ?, current_course_id = ? WHERE id = ?",
            (limits.cognitive_limit, limits.assigned_course_id, student_id)
        )
        conn.commit()
    
    return {"message": f"Student {student_id} limits updated successfully"}

@app.get("/teacher/students/{student_id}/analytics", response_model=StudentAnalytics)
async def get_student_analytics(student_id: int):
    """Get detailed analytics for a student"""
    student = get_student_by_id(student_id)
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get all metrics history for the student
        cursor.execute("""
            SELECT id, student_id, timestamp, gaze_score, face_attention, 
                   cognitive_load, emotional_state, progress
            FROM metrics_history 
            WHERE student_id = ?
            ORDER BY timestamp DESC
            LIMIT 50
        """, (student_id,))
        
        history_data = cursor.fetchall()
        history = [MetricsHistory(**h) for h in history_data]
        
        # Calculate analytics
        if history:
            cognitive_load_history = [h.cognitive_load for h in history]
            engagement_scores = [h.face_attention * 100 for h in history]
            
            # Emotional state distribution
            emotional_counts = {}
            for h in history:
                emotional_counts[h.emotional_state] = emotional_counts.get(h.emotional_state, 0) + 1
            
            average_cognitive_load = sum(cognitive_load_history) / len(cognitive_load_history)
            average_engagement = sum(engagement_scores) / len(engagement_scores)
        else:
            cognitive_load_history = []
            engagement_scores = []
            emotional_counts = {"normal": 1}  # Default
            average_cognitive_load = 0.0
            average_engagement = 0.0
        
        return StudentAnalytics(
            student_id=student_id,
            student_name=student.name,
            progress_history=history,
            cognitive_load_history=cognitive_load_history,
            emotional_state_distribution=emotional_counts,
            engagement_scores=engagement_scores,
            average_cognitive_load=average_cognitive_load,
            average_engagement=average_engagement,
            total_sessions=len(history)
        )

@app.get("/teacher/dashboard/analytics")
async def get_dashboard_analytics():
    """Get comprehensive dashboard analytics"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            
            # Get all students
            cursor.execute("""
                SELECT s.*, c.title as course_title 
                FROM students s 
                LEFT JOIN courses c ON s.current_course_id = c.id
            """)
            students = cursor.fetchall()
            
            # Get all courses
            cursor.execute("SELECT * FROM courses")
            courses = cursor.fetchall()
            
            # Get recent activity (last 10 progress updates) - handle case where table might not exist
            recent_activity = []
            try:
                cursor.execute("""
                    SELECT ph.*, s.name as student_name 
                    FROM metrics_history ph 
                    JOIN students s ON ph.student_id = s.id 
                    ORDER BY ph.timestamp DESC 
                    LIMIT 10
                """)
                recent_activity = cursor.fetchall()
            except Exception as e:
                print(f"Warning: Could not fetch metrics history: {e}")
            
            # Calculate analytics
            total_students = len(students)
            total_courses = len(courses)
            
            # Average progress - handle empty case and ensure proper bounds
            avg_progress = 0.0
            if total_students > 0:
                progress_sum = 0.0
                valid_progress_count = 0
                for student in students:
                    # Find progress column (index 4 based on database structure)
                    if len(student) > 4:
                        progress = student[4] or 0.0
                        # Ensure progress is between 0 and 1, handle cases where it might be stored as percentage
                        if progress > 1.0:  # If stored as percentage (e.g., 50.0 for 50%)
                            progress = progress / 100.0
                        # Clamp to valid range
                        progress = max(0.0, min(1.0, progress))
                        progress_sum += progress
                        valid_progress_count += 1
                
                # Use valid progress count for average, ignore invalid entries
                if valid_progress_count > 0:
                    avg_progress = progress_sum / valid_progress_count
            
            # Engaged students (progress > 50%)
            engaged_students = 0
            for s in students:
                if len(s) > 4:
                    progress = s[4] or 0.0
                    # Apply same bounds checking as above
                    if progress > 1.0:
                        progress = progress / 100.0
                    progress = max(0.0, min(1.0, progress))
                    if progress > 0.5:
                        engaged_students += 1
            
            # Emotional state distribution
            emotional_states = {}
            for s in students:
                # Find emotional state column (index 7 based on database structure)
                state = 'unknown'
                if len(s) > 7:
                    state = s[7] or 'unknown'
                emotional_states[state] = emotional_states.get(state, 0) + 1
            
            # Average cognitive load
            avg_cognitive_load = 80.0  # Default
            if total_students > 0:
                cognitive_sum = 0.0
                for student in students:
                    # Find cognitive limit column (index 6 based on database structure)
                    if len(student) > 6:
                        cognitive_sum += student[6] or 80
                avg_cognitive_load = cognitive_sum / total_students
            
            # Top performers (progress > 80%)
            top_performers = 0
            for s in students:
                if len(s) > 4:
                    progress = s[4] or 0.0
                    # Apply same bounds checking as above
                    if progress > 1.0:
                        progress = progress / 100.0
                    progress = max(0.0, min(1.0, progress))
                    if progress > 0.8:
                        top_performers += 1
            
            # Students needing attention (progress < 30%)
            need_attention = 0
            for s in students:
                if len(s) > 4:
                    progress = s[4] or 0.0
                    # Apply same bounds checking as above
                    if progress > 1.0:
                        progress = progress / 100.0
                    progress = max(0.0, min(1.0, progress))
                    if progress < 0.3:
                        need_attention += 1
            
            return {
                "total_students": total_students,
                "total_courses": total_courses,
                "average_progress": avg_progress * 100,  # Convert to percentage
                "engaged_students": engaged_students,
                "emotional_state_distribution": emotional_states,
                "average_cognitive_load": avg_cognitive_load,
                "top_performers": top_performers,
                "students_need_attention": need_attention,
                "recent_activity": [
                    {
                        "timestamp": activity[2] if len(activity) > 2 else None,
                        "student_name": activity[8] if len(activity) > 8 else 'Unknown',
                        "type": "progress_update",
                        "details": f"Progress: {((activity[3] or 0) * 100):.1f}%" if len(activity) > 3 else "Progress updated"
                    }
                    for activity in recent_activity
                ]
            }
    except Exception as e:
        print(f"Error in dashboard analytics: {e}")
        # Return default values on error
        return {
            "total_students": 0,
            "total_courses": 0,
            "average_progress": 0.0,
            "engaged_students": 0,
            "emotional_state_distribution": {"normal": 1},
            "average_cognitive_load": 80.0,
            "top_performers": 0,
            "students_need_attention": 0,
            "recent_activity": []
        }

# AUTHENTICATION ENDPOINTS

@app.post("/auth/register", response_model=UserResponse)
async def register_user(user: UserRegister):
    """Register a new user (student or teacher)"""
    if user.role not in ["student", "teacher"]:
        raise HTTPException(status_code=400, detail="Role must be 'student' or 'teacher'")
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Insert new user
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (?, ?, ?, ?)",
            (user.name, user.email, user.password, user.role)
        )
        conn.commit()
        
        # Get created user
        cursor.execute("SELECT * FROM users WHERE id = last_insert_rowid()")
        user_data = cursor.fetchone()
        
        # If user is a student, create corresponding student profile
        if user.role == "student":
            cursor.execute(
                "INSERT INTO students (user_id, name) VALUES (?, ?)",
                (user_data["id"], user.name)
            )
        # If user is a teacher, create corresponding teacher profile
        elif user.role == "teacher":
            cursor.execute(
                "INSERT INTO teachers (user_id) VALUES (?)",
                (user_data["id"],)
            )
        conn.commit()
        
        # Update credentials.csv
        try:
            import csv
            from datetime import datetime
            with open('credentials.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([user.email, user.password, user.role, datetime.now().isoformat()])
        except Exception as e:
            print(f"Warning: Could not update credentials.csv: {e}")
        
        return UserResponse(**user_data)

@app.post("/auth/login", response_model=LoginResponse)
async def login_user(user: UserLogin):
    """Login user and return role and user_id"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? AND password_hash = ?", (user.email, user.password))
        user_data = cursor.fetchone()
        
        if not user_data:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        role = user_data["role"]
        user_id = user_data["id"]
        
        if role == "student":
            cursor.execute("SELECT id FROM students WHERE user_id = ?", (user_id,))
            student_data = cursor.fetchone()
            if not student_data:
                raise HTTPException(status_code=404, detail="Student record not found")
            return LoginResponse(
                status="ok", 
                role=role, 
                user_id=student_data["id"], 
                user_name=user_data["name"],
                student_id=student_data["id"]
            )
        elif role == "teacher":
            cursor.execute("SELECT id FROM teachers WHERE user_id = ?", (user_id,))
            teacher_data = cursor.fetchone()
            if not teacher_data:
                raise HTTPException(status_code=404, detail="Teacher record not found")
            return LoginResponse(
                status="ok", 
                role=role, 
                user_id=teacher_data["id"], 
                user_name=user_data["name"],
                teacher_id=teacher_data["id"]
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid user role")
@app.post("/course-pdf-content")
async def extract_course_pdf_content(request: dict):
    """Extract text content from course PDF"""
    pdf_url = request.get("pdf_url")
    
    if not pdf_url:
        raise HTTPException(status_code=400, detail="PDF URL is required")
    
    try:
        # Convert URL to file path
        if pdf_url.startswith("/"):
            pdf_path = os.path.join(os.path.dirname(__file__), pdf_url.lstrip("/"))
        else:
            pdf_path = pdf_url
        
        print(f"Looking for PDF at: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail=f"PDF file not found at {pdf_path}")
        
        # Try to extract text from PDF
        try:
            import PyPDF2
            print("Using PyPDF2 for extraction")
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text_content += page.extract_text() + "\n"
                
                extracted_text = text_content.strip()
                
                if not extracted_text:
                    raise ValueError("No text could be extracted from PDF")
                
                print(f"Successfully extracted {len(extracted_text)} characters")
                return {"content": extracted_text}
                
        except ImportError:
            print("PyPDF2 not installed, trying pdfplumber")
            
            # Fallback to pdfplumber if available
            try:
                import pdfplumber
                
                with pdfplumber.open(pdf_path) as pdf:
                    text_content = ""
                    for page in pdf.pages:
                        text_content += page.extract_text() + "\n"
                    
                    extracted_text = text_content.strip()
                    
                    if not extracted_text:
                        raise ValueError("No text could be extracted from PDF")
                    
                    print(f"Successfully extracted {len(extracted_text)} characters using pdfplumber")
                    return {"content": extracted_text}
                    
            except ImportError:
                raise HTTPException(
                    status_code=500, 
                    detail="PDF extraction libraries not installed. Please install PyPDF2 or pdfplumber."
                )
        except Exception as extraction_error:
            print(f"PDF extraction failed: {extraction_error}")
            raise HTTPException(
                status_code=500, 
                detail=f"Failed to extract text from PDF: {str(extraction_error)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error in PDF extraction: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import webbrowser
    import threading
    import time
    
    # Function to open browser after server starts
    def open_browser():
        time.sleep(2)  # Wait for server to start
        webbrowser.open('http://localhost:8000/frontend/auth.html')
    
    # Start browser opening in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)
