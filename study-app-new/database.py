import sqlite3
import os
from contextlib import contextmanager

DATABASE_URL = "study_app.db"

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

@contextmanager
def get_db():
    """Context manager for database operations"""
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()

def init_database():
    """Initialize database with required tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table for authentication
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK (role IN ('student', 'teacher')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
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
        )
    """)
    
    # Create teachers table for teacher-specific data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            department TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    
    # Create courses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            video_url TEXT,
            pdf_url TEXT,
            difficulty_level TEXT DEFAULT 'beginner',
            duration_minutes INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create student_courses table (many-to-many relationship)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completion_date TIMESTAMP,
            status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'dropped')),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            UNIQUE(student_id, course_id)
        )
    """)
    
    # Create notes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
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
        )
    """)
    
    # Create metrics_history table for analytics
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metrics_history (
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
        )
    """)
    
    # Create indexes for performance (after migration to ensure all columns exist)
    # These will be created again in migrate_database() if needed
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_user_id ON students(user_id)")
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_teachers_user_id ON teachers(user_id)")
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_courses_student_id ON student_courses(student_id)")
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_student_courses_course_id ON student_courses(course_id)")
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_student_id ON notes(student_id)")
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_notes_course_id ON notes(course_id)")
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_history_student_id ON metrics_history(student_id)")
    # cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_history_timestamp ON metrics_history(timestamp)")
    
    # Insert sample data
    cursor.execute("SELECT COUNT(*) FROM courses")
    if cursor.fetchone()[0] == 0:
        sample_courses = [
            ("Introduction to Python", "Learn the basics of Python programming", "sample uploads/computer.mp4", "sample uploads/ai-vs-ml.pdf", "beginner", 120),
            ("Data Science Fundamentals", "Understanding data analysis and machine learning concepts", "sample uploads/data-science.mp4", "sample uploads/ai-vs-ml.pdf", "intermediate", 180),
            ("AI Research Methods", "Advanced research techniques in artificial intelligence", "sample uploads/research.mp4", "sample uploads/ai-vs-ml.pdf", "advanced", 200),
            ("Computer Vision Basics", "Introduction to computer vision and image processing", "sample uploads/computer.mp4", "sample uploads/ai-vs-ml.pdf", "intermediate", 150)
        ]
        cursor.executemany("INSERT INTO courses (title, description, video_url, pdf_url, difficulty_level, duration_minutes) VALUES (?, ?, ?, ?, ?, ?)", sample_courses)
    
    # Insert sample users
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        sample_users = [
            ("Alice Johnson", "alice@example.com", "hashed_password_1", "student"),
            ("Bob Smith", "bob@example.com", "hashed_password_2", "student"),
            ("Carol Davis", "carol@example.com", "hashed_password_3", "student"),
            ("Dr. Wilson", "wilson@example.com", "hashed_password_4", "teacher")
        ]
        cursor.executemany("INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)", sample_users)
        
        # Get the inserted user IDs
        cursor.execute("SELECT id FROM users WHERE role = 'student'")
        student_users = cursor.fetchall()
        
        cursor.execute("SELECT id FROM users WHERE role = 'teacher'")
        teacher_users = cursor.fetchall()
        
        # Insert students linked to users
        if student_users:
            sample_students = [
                (student_users[0][0], "Alice Johnson", "alice@example.com", "hashed_password_1", 70, 0.0, "normal", None),
                (student_users[1][0], "Bob Smith", "bob@example.com", "hashed_password_2", 60, 0.3, "neutral", 1),
                (student_users[2][0], "Carol Davis", "carol@example.com", "hashed_password_3", 80, 0.0, "normal", None)
            ]
            cursor.executemany("INSERT INTO students (user_id, name, email, password_hash, cognitive_limit, progress, emotional_state, current_course_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", sample_students)
        
        # Insert teachers linked to users
        if teacher_users:
            sample_teachers = [
                (teacher_users[0][0], "Dr. Wilson", "wilson@example.com", "hashed_password_4", "Computer Science")
            ]
            cursor.executemany("INSERT INTO teachers (user_id, name, email, password_hash, department) VALUES (?, ?, ?, ?, ?)", sample_teachers)
        
        # Enroll students in courses
        cursor.execute("SELECT id FROM students")
        all_students = cursor.fetchall()
        cursor.execute("SELECT id FROM courses")
        all_courses = cursor.fetchall()
        
        if all_students and all_courses:
            enrollments = []
            for student in all_students[:2]:  # Enroll first 2 students
                for course in all_courses[:2]:  # Enroll in first 2 courses
                    enrollments.append((student[0], course[0]))
            
            cursor.executemany("INSERT INTO student_courses (student_id, course_id) VALUES (?, ?)", enrollments)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

def migrate_database():
    """Apply database migrations to match documented structure"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if we need to migrate from old structure
        cursor.execute("PRAGMA table_info(users)")
        users_columns = [column[1] for column in cursor.fetchall()]
        
        # Update users table if needed
        if 'password' in users_columns and 'password_hash' not in users_columns:
            print("Migrating users table: renaming password to password_hash...")
            cursor.execute("ALTER TABLE users RENAME COLUMN password TO password_hash")
        
        # Check students table structure
        cursor.execute("PRAGMA table_info(students)")
        students_columns = [column[1] for column in cursor.fetchall()]
        
        # Add missing columns to students table
        missing_student_columns = []
        required_student_columns = ['user_id', 'name', 'email', 'password_hash', 'cognitive_limit', 'progress', 'emotional_state', 'current_course_id', 'created_at']
        
        for col in required_student_columns:
            if col not in students_columns:
                missing_student_columns.append(col)
        
        if missing_student_columns:
            print(f"Adding missing columns to students table: {missing_student_columns}")
            for col in missing_student_columns:
                if col == 'user_id':
                    cursor.execute("ALTER TABLE students ADD COLUMN user_id INTEGER")
                elif col == 'email':
                    cursor.execute("ALTER TABLE students ADD COLUMN email TEXT")
                elif col == 'password_hash':
                    cursor.execute("ALTER TABLE students ADD COLUMN password_hash TEXT")
                elif col == 'cognitive_limit':
                    cursor.execute("ALTER TABLE students ADD COLUMN cognitive_limit INTEGER DEFAULT 70")
                elif col == 'progress':
                    cursor.execute("ALTER TABLE students ADD COLUMN progress REAL DEFAULT 0.0")
                elif col == 'emotional_state':
                    cursor.execute("ALTER TABLE students ADD COLUMN emotional_state TEXT DEFAULT 'normal'")
                elif col == 'current_course_id':
                    cursor.execute("ALTER TABLE students ADD COLUMN current_course_id INTEGER")
                elif col == 'created_at':
                    cursor.execute("ALTER TABLE students ADD COLUMN created_at TIMESTAMP")
                    # SQLite limitation: set current timestamp for existing rows
                    cursor.execute("UPDATE students SET created_at = datetime('now') WHERE created_at IS NULL")
        
        # Check if student_courses table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='student_courses'")
        if not cursor.fetchone():
            print("Creating student_courses table...")
            cursor.execute("""
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
                )
            """)
        
        # Update courses table with missing columns
        cursor.execute("PRAGMA table_info(courses)")
        courses_columns = [column[1] for column in cursor.fetchall()]
        
        missing_course_columns = []
        required_course_columns = ['difficulty_level', 'duration_minutes', 'created_at']
        
        for col in required_course_columns:
            if col not in courses_columns:
                missing_course_columns.append(col)
        
        if missing_course_columns:
            print(f"Adding missing columns to courses table: {missing_course_columns}")
            for col in missing_course_columns:
                if col == 'difficulty_level':
                    cursor.execute("ALTER TABLE courses ADD COLUMN difficulty_level TEXT DEFAULT 'beginner'")
                elif col == 'duration_minutes':
                    cursor.execute("ALTER TABLE courses ADD COLUMN duration_minutes INTEGER")
                elif col == 'created_at':
                    cursor.execute("ALTER TABLE courses ADD COLUMN created_at TIMESTAMP")
                    # SQLite limitation: set current timestamp for existing rows
                    cursor.execute("UPDATE courses SET created_at = datetime('now') WHERE created_at IS NULL")
        
        # Update notes table structure
        cursor.execute("PRAGMA table_info(notes)")
        notes_columns = [column[1] for column in cursor.fetchall()]
        
        missing_note_columns = []
        required_note_columns = ['course_id', 'title', 'content', 'file_type', 'updated_at']
        
        for col in required_note_columns:
            if col not in notes_columns:
                missing_note_columns.append(col)
        
        if missing_note_columns:
            print(f"Adding missing columns to notes table: {missing_note_columns}")
            for col in missing_note_columns:
                if col == 'course_id':
                    cursor.execute("ALTER TABLE notes ADD COLUMN course_id INTEGER")
                elif col == 'title':
                    cursor.execute("ALTER TABLE notes ADD COLUMN title TEXT")
                elif col == 'content':
                    cursor.execute("ALTER TABLE notes ADD COLUMN content TEXT")
                elif col == 'file_type':
                    cursor.execute("ALTER TABLE notes ADD COLUMN file_type TEXT")
                elif col == 'updated_at':
                    cursor.execute("ALTER TABLE notes ADD COLUMN updated_at TIMESTAMP")
                    # SQLite limitation: set current timestamp for existing rows
                    cursor.execute("UPDATE notes SET updated_at = datetime('now') WHERE updated_at IS NULL")
        
        # Update metrics_history table
        cursor.execute("PRAGMA table_info(metrics_history)")
        metrics_columns = [column[1] for column in cursor.fetchall()]
        
        if 'session_duration' not in metrics_columns:
            print("Adding session_duration to metrics_history table...")
            cursor.execute("ALTER TABLE metrics_history ADD COLUMN session_duration REAL")
        
        # Create indexes if they don't exist
        indexes_to_create = [
            ("idx_students_user_id", "students(user_id)"),
            ("idx_teachers_user_id", "teachers(user_id)"),
            ("idx_student_courses_student_id", "student_courses(student_id)"),
            ("idx_student_courses_course_id", "student_courses(course_id)"),
            ("idx_notes_student_id", "notes(student_id)"),
            ("idx_notes_course_id", "notes(course_id)"),
            ("idx_metrics_history_student_id", "metrics_history(student_id)"),
            ("idx_metrics_history_timestamp", "metrics_history(timestamp)")
        ]
        
        for index_name, index_def in indexes_to_create:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='index' AND name='{index_name}'")
            if not cursor.fetchone():
                print(f"Creating index: {index_name}")
                cursor.execute(f"CREATE INDEX {index_name} ON {index_def}")
        
        conn.commit()
        print("Database migration completed successfully!")
        
    except Exception as e:
        print(f"Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()
    migrate_database()
