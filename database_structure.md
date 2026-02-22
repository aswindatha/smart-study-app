# Database Structure Documentation

## Overview
This document describes the database schema for the Smart Learning App, including table structures, relationships, and their usage throughout the application.

## Tables

### 1. Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('student', 'teacher')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Stores authentication and basic user information for both students and teachers.

### 2. Students Table
```sql
CREATE TABLE students (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    cognitive_limit INTEGER DEFAULT 70,
    progress REAL DEFAULT 0.0,
    emotional_state TEXT DEFAULT 'normal',
    current_course_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (current_course_id) REFERENCES courses(id) ON DELETE SET NULL
);
```

**Purpose**: Extended student-specific information including learning metrics and current progress.

### 3. Teachers Table
```sql
CREATE TABLE teachers (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    department TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Purpose**: Teacher-specific information for course management and student monitoring.

### 4. Courses Table
```sql
CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    video_url TEXT,
    pdf_url TEXT,
    difficulty_level TEXT DEFAULT 'beginner',
    duration_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Purpose**: Course content and metadata for learning materials.

### 5. Student_Courses Table (Many-to-Many)
```sql
CREATE TABLE student_courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completion_date TIMESTAMP,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'dropped')),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    UNIQUE(student_id, course_id)
);
```

**Purpose**: Tracks which students are enrolled in which courses and their enrollment status.

### 6. Notes Table
```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    course_id INTEGER,
    title TEXT NOT NULL,
    content TEXT,
    file_path TEXT,
    file_type TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE SET NULL
);
```

**Purpose**: Student notes and uploaded documents, optionally associated with specific courses.

### 7. Metrics_History Table
```sql
CREATE TABLE metrics_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gaze_score REAL NOT NULL,
    face_attention REAL NOT NULL,
    cognitive_load REAL NOT NULL,
    emotional_state TEXT NOT NULL,
    progress REAL NOT NULL,
    session_duration REAL,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
```

**Purpose**: Historical tracking of student learning analytics and progress over time.

## Relationships and Their Purpose

### 1. Users → Students (One-to-One)
**Relationship**: `students.user_id` → `users.id`

**Why Needed**: 
- Separates authentication concerns from student-specific data
- Allows for future expansion to other user types
- Maintains data normalization principles

**Where Used**:
- **Authentication**: Login validation uses `users` table
- **Student Dashboard**: Queries `students` table for learning metrics
- **Progress Tracking**: Updates student-specific progress data

**Example Query**:
```sql
-- Get student with user info for dashboard
SELECT s.*, u.email, u.created_at 
FROM students s 
JOIN users u ON s.user_id = u.id 
WHERE s.id = ?;
```

### 2. Users → Teachers (One-to-One)
**Relationship**: `teachers.user_id` → `users.id`

**Why Needed**:
- Single authentication system for both roles
- Teacher-specific data (department, etc.) kept separate
- Maintains referential integrity

**Where Used**:
- **Teacher Dashboard**: Teacher profile and course management
- **Course Assignment**: Teachers can manage their assigned courses
- **Student Analytics**: Teachers view student progress data

**Example Query**:
```sql
-- Get teacher with user info
SELECT t.*, u.email, u.name 
FROM teachers t 
JOIN users u ON t.user_id = u.id 
WHERE t.id = ?;
```

### 3. Students → Courses (Many-to-Many via student_courses)
**Relationship**: `student_courses.student_id` → `students.id` and `student_courses.course_id` → `courses.id`

**Why Needed**:
- Students can enroll in multiple courses
- Courses can have multiple students
- Tracks enrollment status and dates

**Where Used**:
- **Course Enrollment**: Adding/removing students from courses
- **Progress Tracking**: Per-course progress for each student
- **Learning Analytics**: Course-specific metrics

**Example Query**:
```sql
-- Get all courses for a student
SELECT c.*, sc.enrollment_date, sc.status 
FROM courses c 
JOIN student_courses sc ON c.id = sc.course_id 
WHERE sc.student_id = ? AND sc.status = 'active';
```

### 4. Students → Current Course (One-to-Many)
**Relationship**: `students.current_course_id` → `courses.id`

**Why Needed**:
- Tracks which course the student is currently studying
- Enables quick access to current learning context
- Supports resume functionality

**Where Used**:
- **Learning Hub**: Shows current course and materials
- **Progress Updates**: Updates progress for current course
- **Analytics**: Associates metrics with current course

**Example Query**:
```sql
-- Get student's current course
SELECT c.* 
FROM courses c 
JOIN students s ON c.id = s.current_course_id 
WHERE s.id = ?;
```

### 5. Notes → Students (Many-to-One)
**Relationship**: `notes.student_id` → `students.id`

**Why Needed**:
- Notes belong to specific students
- Enables personal note management
- Supports note sharing and privacy

**Where Used**:
- **Note Management**: CRUD operations for student notes
- **Chat Integration**: Notes used as context for AI chat
- **Course Association**: Notes optionally linked to courses

**Example Query**:
```sql
-- Get all notes for a student
SELECT * FROM notes 
WHERE student_id = ? 
ORDER BY updated_at DESC;
```

### 6. Notes → Courses (Many-to-One, Optional)
**Relationship**: `notes.course_id` → `courses.id`

**Why Needed**:
- Associates notes with specific course content
- Enables course-specific note filtering
- Supports contextual learning

**Where Used**:
- **Course Notes**: Show notes for current course
- **Note Organization**: Filter notes by course
- **Study Context**: Relevant notes for current study session

**Example Query**:
```sql
-- Get notes for specific course
SELECT * FROM notes 
WHERE student_id = ? AND course_id = ? 
ORDER BY updated_at DESC;
```

### 7. Metrics_History → Students (Many-to-One)
**Relationship**: `metrics_history.student_id` → `students.id`

**Why Needed**:
- Tracks learning analytics over time
- Enables progress analysis and trending
- Supports personalized learning recommendations

**Where Used**:
- **Analytics Dashboard**: Historical progress visualization
- **Teacher Reports**: Student performance analytics
- **Adaptive Learning**: System adjusts based on historical data

**Example Query**:
```sql
-- Get recent metrics for student
SELECT * FROM metrics_history 
WHERE student_id = ? 
ORDER BY timestamp DESC 
LIMIT 50;
```

## Database Usage in Application

### Frontend Components

#### Student Dashboard (`student_dashboard.html`)
- **Authentication**: Uses `users` table for login
- **Profile Data**: Queries `students` table for progress and metrics
- **Course Loading**: Gets courses via `student_courses` junction table
- **Notes Management**: CRUD operations on `notes` table
- **Analytics**: Reads/writes `metrics_history` table

#### Teacher Dashboard (`teacher_dashboard.html`)
- **Authentication**: Uses `users` table for login
- **Student Management**: Queries `students` and related tables
- **Course Analytics**: Aggregates data from `metrics_history`
- **Progress Monitoring**: Views student progress across courses

#### Authentication (`auth.html`)
- **User Registration**: Inserts into `users` and role-specific tables
- **Login Validation**: Queries `users` table with role verification

### Backend Components

#### Main Application (`main.py`)
- **Student Endpoints**: `/students/{id}/*` operations on student data
- **Course Endpoints**: `/courses/*` operations on course data
- **Analytics Endpoints**: `/analyze_image` updates `metrics_history`
- **Progress Updates**: `/students/{id}/update_progress` updates multiple tables

#### Database Operations (`database.py`)
- **Connection Management**: Handles database connections and transactions
- **CRUD Operations**: Basic create, read, update, delete operations
- **Data Validation**: Ensures data integrity before database operations

## Data Flow Examples

### Student Learning Session
1. **Login**: Authenticate against `users` table
2. **Load Dashboard**: Get student data from `students` table
3. **Select Course**: Query `student_courses` and `courses` tables
4. **Start Video**: Update `students.current_course_id`
5. **Analytics Tracking**: Insert real-time data into `metrics_history`
6. **Take Notes**: Insert/update records in `notes` table
7. **Pause Video**: Update progress in `students` table
8. **Complete Course**: Update `student_courses` status

### Teacher Monitoring Session
1. **Login**: Authenticate against `users` table
2. **Load Student List**: Query `students` with course relationships
3. **View Analytics**: Aggregate data from `metrics_history`
4. **Assign Courses**: Update `student_courses` table
5. **Set Limits**: Update `students.cognitive_limit`

## Performance Considerations

### Indexes
```sql
-- Recommended indexes for performance
CREATE INDEX idx_students_user_id ON students(user_id);
CREATE INDEX idx_teachers_user_id ON teachers(user_id);
CREATE INDEX idx_student_courses_student_id ON student_courses(student_id);
CREATE INDEX idx_student_courses_course_id ON student_courses(course_id);
CREATE INDEX idx_notes_student_id ON notes(student_id);
CREATE INDEX idx_notes_course_id ON notes(course_id);
CREATE INDEX idx_metrics_history_student_id ON metrics_history(student_id);
CREATE INDEX idx_metrics_history_timestamp ON metrics_history(timestamp);
```

### Query Optimization
- Use JOINs instead of multiple queries where possible
- Implement pagination for large datasets (metrics_history)
- Cache frequently accessed data (course lists, student info)
- Use transactions for multi-table operations

## Data Integrity

### Constraints
- **Foreign Keys**: Ensure referential integrity
- **UNIQUE Constraints**: Prevent duplicate enrollments and emails
- **CHECK Constraints**: Validate enum values and ranges
- **NOT NULL**: Ensure required data is present

### Cascade Operations
- **ON DELETE CASCADE**: Remove dependent records when parent is deleted
- **ON DELETE SET NULL**: Maintain data when optional relationships are broken

## Future Enhancements

### Planned Tables
1. **Quiz_Table**: For assessments and testing
2. **Assignments_Table**: For homework and projects
3. **Discussions_Table**: For course discussions
4. **Certificates_Table**: For course completion awards

### Relationship Extensions
1. **Course_Prerequisites**: Self-referencing course relationships
2. **Learning_Paths**: Structured course sequences
3. **Study_Groups**: Collaborative learning groups
4. **Achievements**: Gamification elements

This database structure supports the current functionality while providing flexibility for future enhancements and maintaining data integrity throughout the application.