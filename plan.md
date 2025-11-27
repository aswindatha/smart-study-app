APP OVERVIEW

A Smart Study App that allows students to upload notes/books, generate summaries, MCQs, flashcards, explanations, and track progress. Teachers get additional admin tools. Uses AI models locally or via API.

✅ 2. APP FOLDER STRUCTURE (3 MAIN FOLDERS ONLY)
smart_study_app/
│
├── api/
│   ├── __init__.py
│   ├── app.py
│   ├── authentication.py
│   ├── ai_engine.py
│   ├── database.py
│   ├── routes/
│   │   ├── user_routes.py
│   │   ├── study_routes.py
│   │   ├── admin_routes.py
│   │   └── progress_routes.py
│   └── utils/
│       ├── pdf_reader.py
│       ├── file_manager.py
│       └── token_manager.py
│
├── frontend/
│   ├── home.py
│   ├── login.py
│   ├── register.py
│   ├── dashboard.py
│   ├── study_tools.py
│   ├── upload_notes.py
│   ├── flashcards.py
│   ├── mcq_generator.py
│   ├── summary_generator.py
│   ├── progress.py
│   ├── teacher_dashboard.py
│   └── components/
│       ├── navbar.py
│       ├── sidebar.py
│       └── style.css
│
├── images/
│   ├── logo.png
│   ├── banners/
│   └── icons/
│
├── smartstudy.db
└── requirements.txt

✅ 3. USER ROLES
1. Student

Upload notes / PDFs / text

Generate summary

Generate MCQs

Generate flashcards

Get explanations

Track progress

Bookmark materials

2. Teacher

Includes all student features +

Add course materials

Upload bulk study content

Create test papers

View student activity analytics

3. Admin

Includes all teacher features +

Manage users

Approve teacher roles

System logs

Backup/restore DB

✅ 4. DATABASE DESIGN (SQLite)
✅ Tables
1. users
id	name	email	password	role	created_at
2. study_materials

| id | user_id | title | file_path | extracted_text | uploaded_at |

3. ai_outputs

| id | material_id | type (summary/mcq/flashcard/explanation) | output_text | created_at |

4. progress

| id | user_id | material_id | completed_percent | last_accessed |

5. logs

| id | user_id | action | timestamp |

✅ 5. BACKEND (FLASK API) DESIGN
✅ api/app.py

Handles Flask app initialization, CORS, route registration.

✅ api/authentication.py

Login

Register

Token generation

Token validation

✅ api/ai_engine.py

Functions:

generate_summary(text)

generate_mcqs(text)

generate_flashcards(text)

generate_explanation(question, text)

Uses local or cloud LLM.

✅ api/pdf_reader.py

Extract text from:

PDF

Images (OCR optional)

Text files

✅ api/routes/user_routes.py

APIs:

/register

/login

/profile

/update_password

✅ api/routes/study_routes.py

APIs:

/upload_note

/extract_text

/generate_summary

/generate_mcq

/generate_flashcards

/explain

✅ api/routes/progress_routes.py

/save_progress

/get_progress

✅ api/routes/admin_routes.py

/all_users

/approve_teacher

/delete_user

/system_logs

✅ 6. FRONTEND (STREAMLIT) DESIGN

Streamlit communicates with Flask API using requests.

✅ Pages
1. login.py

login UI

token saved in session

2. register.py

create new account

3. dashboard.py (Student)

Shows:

Recent materials

AI tools

Progress overview

4. upload_notes.py

Upload PDF / text
Calls:

/upload_note

/extract_text

5. study_tools.py

UI page linking:

Summary

Flashcards

MCQs

Explanation

6. summary_generator.py

UI:

select material

generate summary

save summary

7. mcq_generator.py

UI:

MCQ generation with difficulty

8. flashcards.py

UI:

Display flashcards

Shuffle mode

9. progress.py

Graph-based student learning analytics.

✅ Teacher Pages
10. teacher_dashboard.py

Upload course materials

See student analytics

Create tests

✅ 7. APP LOGIC FLOW
✅ 1. User opens app → Login/Register

Streamlit → Flask API

✅ 2. Dashboard loads based on role

If student → student dashboard

If teacher → teacher dashboard

If admin → admin panel

✅ 3. User uploads study material

File stored in /images/uploads

Text extracted → stored in DB

✅ 4. User performs AI operations

User selects:

Summary

Flashcards

MCQs

Explanation

Flask AI engine returns output.

✅ 5. Progress tracking

Whenever user:

Views output

Completes test

Reads flashcards

→ Progress updates in DB.

✅ 6. Teachers manage classes & content
✅ 7. Admin manages users & logs
✅ 8. API INPUT/OUTPUT EXAMPLES
✅ POST /generate_summary

Input

{
  "material_id": 21,
  "token": "jwt_token_here"
}


Output

{
  "summary": "This chapter explains...",
  "status": "success"
}

✅ 9. SECURITY

Role-based API filtering

File validation
