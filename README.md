# Smart Learning App

A minimal Smart Learning Application with cognitive load tracking and personalized learning features.

## Features

### Student Features
- 📊 **Dashboard**: View current course, progress, emotional state, and cognitive load
- 📚 **Course Management**: Browse and start courses
- 🧠 **Real-time Progress Tracking**: Live eye-tracking and attention monitoring
- 📝 **Notes Upload**: Upload TXT/PDF files with automatic summarization
- 🤖 **Learning Assistant**: Rule-based chatbot for learning support

### Real Camera Eye-Tracking
- 📹 **Live Camera Capture**: Real-time video feed from user's camera
- 👁️ **Face Detection**: OpenCV-based face and eye detection
- 🎯 **Gaze Tracking**: Analyzes eye position and openness for attention scoring
- 😊 **Emotion Detection**: Basic emotional state detection from facial features
- 🔄 **Auto-Tracking**: Continuous analysis every 3 seconds option
- 📊 **Cognitive Load Calculation**: Real-time cognitive load based on eye metrics

### Cognitive Load & Eye-Tracking
- **Real-time Analysis**: Uses actual camera input instead of mock data
- **Face Detection**: Haar cascade classifiers for face and eye detection
- **Gaze Score**: Calculated from eye position, size, and openness
- **Attention Score**: Based on face position, size, and centering
- **Emotional State**: Detected from facial feature variance
- **Personalized Recommendations**: Based on real engagement metrics

## Project Structure

```
/app
├── main.py              # FastAPI server with all endpoints
├── database.py          # SQLite database setup and connection
├── models.py            # Pydantic models for API
├── utils.py             # Utility functions (cognitive load, summarization)
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── frontend/
    └── index.html      # Testing interface
```

## Database Schema

### Tables
- **students**: id, name, current_course_id, progress, cognitive_limit, emotional_state
- **courses**: id, title, description, video_url, pdf_url
- **notes**: id, student_id, file_path, summary

### Sample Data
- 3 students (Alice, Bob, Carol)
- 4 sample courses (Python, Data Structures, Web Dev, Database)

### API Endpoints

### Student Endpoints
1. `GET /students/{id}/dashboard` - Get student dashboard
2. `GET /courses` - List all courses
3. `POST /students/{id}/start_course/{course_id}` - Start a course
4. `POST /students/{id}/update_progress` - Update learning progress
5. `POST /students/{id}/upload_notes` - Upload and summarize notes
6. `GET /students/{id}/notes` - Get student's notes
7. `POST /chatbot` - Chat with learning assistant
8. `POST /analyze_image` - **NEW**: Real-time face and gaze analysis

### Real Camera Features
- **Live Video Feed**: Direct camera capture in browser
- **Face Detection**: OpenCV Haar cascade classifiers
- **Eye Tracking**: Real-time eye position and openness analysis
- **Emotion Detection**: Basic facial feature analysis
- **Auto-Tracking**: Continuous monitoring every 3 seconds
- **Real-time Metrics**: Immediate cognitive load and engagement calculation

## Installation & Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize database:**
   ```bash
   python database.py
   ```

3. **Run the server:**
   ```bash
   python main.py
   ```
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Open the testing interface:**
   - Open `frontend/index.html` in your browser
   - Or visit `http://localhost:8000/docs` for Swagger UI

## Testing the App

### Using the Frontend Interface
1. Open `frontend/index.html` in your browser
2. Use the tabs to test different features:
   - **Dashboard**: View student information and recommendations
   - **Courses**: Browse courses and start learning
   - **Learning**: Simulate eye-tracking and update progress
   - **Notes Upload**: Upload TXT/PDF files for summarization
   - **Chatbot**: Test the rule-based learning assistant

### Using API Directly
```bash
# Get dashboard for student 1
curl http://localhost:8000/students/1/dashboard

# Get all courses
curl http://localhost:8000/courses

# Start course 1 for student 1
curl -X POST http://localhost:8000/students/1/start_course/1

# Update progress
curl -X POST http://localhost:8000/students/1/update_progress \
  -H "Content-Type: application/json" \
  -d '{"time_spent": 30, "gaze_score": 0.7, "face_attention_score": 0.8}'
```

## Cognitive Load Algorithm

The system uses simplified cognitive load calculation:
- **Cognitive Load** = (1 - gaze_score) × 100
- **Emotional State**: 
  - "stress" if cognitive_load > student's cognitive_limit
  - "normal" if cognitive_load > 70% of limit
  - "relaxed" otherwise
- **Engagement** = face_attention_score × 100

## File Upload Support

- **TXT files**: Direct text extraction
- **PDF files**: Text extraction using PyPDF2
- **Automatic summarization**: Extractive summarization with sentence scoring
- **File storage**: Uploaded files saved to `uploads/` directory

## Next Steps (Phase 2)

- Teacher features and dashboard
- Enhanced frontend with better UI
- Advanced cognitive load algorithms
- Real eye-tracking integration
- More sophisticated chatbot with ML

## Technologies Used

- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **File Processing**: PyPDF2
- **API Documentation**: Swagger UI (built-in)



### key metrics 

# 👀 Gaze Score (0-1):

Eye tracking accuracy during learning
1.0 = perfect focus, 0.0 = distracted/looking away


# 👤 Face Attention Score (0-1):

Face detection and positioning quality
1.0 = centered/engaged, 0.0 = no face detected


# ⚡ Cognitive Load (%):

Current mental effort required (15-95%)
Calculated from gaze score + student's limit
High load = stressed, low load = bored


# 😊 Emotional State:

focused - optimal learning zone
stressed/overwhelmed - too much load
relaxed/bored - too little load
neutral - baseline state


# 📈 Engagement Level (%):

Overall participation score (10-95%)
Based on face attention + natural variation


# 🎯 Progress (%):

Course completion percentage
Updated based on time spent + engagement + cognitive factors


# ⏱️ Session Duration:

Time spent in current learning session
Affects progress calculation


# 📊 Metrics History:

Stores all above metrics over time
Used for analytics and progress tracking