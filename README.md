# Smart Study App

An AI-powered study application with cognitive load monitoring and adaptive learning features, built with Flask API backend and Streamlit frontend.

## Features

- **User Management**: Registration, login, role-based access (Student, Teacher, Admin)
- **Study Material Upload**: Support for PDFs and text files with automatic text extraction
- **AI Tools**: Generate summaries, MCQs, flashcards, and explanations using local AI models
- **Progress Tracking**: Monitor learning progress with analytics dashboards
- **Cognitive Monitoring**: Real-time eye-tracking, emotional analysis, and cognitive load assessment
- **Adaptive Learning**: Personalized recommendations based on cognitive state and performance
- **Secure Authentication**: JWT-based auth with role-based permissions

## Tech Stack

- **Backend**: Flask, SQLite, JWT, OpenCV, DeepFace, PyPDF2
- **Frontend**: Streamlit, Plotly, WebRTC
- **AI**: Local LLM integration (placeholders), cognitive analysis
- **Database**: SQLite with tables for users, materials, AI outputs, progress, cognitive data

## Setup

### Prerequisites
- Python 3.8+
- Webcam access (for cognitive features)
- pip package manager

### Installation

1. **Clone and navigate**:
   ```
   cd smart_study_app/
   ```

2. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Start the application** (runs both Flask API and Streamlit frontend):
   ```
   streamlit run smart_study_app/app.py
   ```

   This command automatically initializes the database, starts the Flask API in the background, and launches the Streamlit app. No separate steps are needed for the API.

4. **(Optional) Populate sample data**:
   ```
   python populate_sample_data.py
   ```

### Manual Startup (if needed)
If you prefer separate terminals:
- Initialize database: `python smart_study_app/api/database.py`
- Run Flask API: `python smart_study_app/api/app.py`
- Run Streamlit: `streamlit run app.py`

## Usage

### Basic Workflow
1. **Register/Login**: Create account or sign in
2. **Upload Materials**: Add PDFs/text files to extract content
3. **Generate Content**: Use AI tools for summaries, questions, flashcards
4. **Track Progress**: Monitor completion and performance
5. **Cognitive Monitoring** (Optional): Enable webcam for real-time analysis
6. **Get Recommendations**: Receive personalized learning suggestions

### User Roles
- **Student**: Upload materials, generate content, track progress
- **Teacher**: All student features + view student analytics, manage content
- **Admin**: All features + user management, system logs, backups

### Key Pages
- **Home**: Overview and quick start guide
- **Dashboard**: Recent materials and AI outputs
- **Study Tools**: Unified interface for AI generation
- **Upload Notes**: File upload and text extraction
- **Progress**: Analytics and completion tracking
- **Cognitive Dashboard**: Mental state monitoring charts
- **Attention Meter**: Real-time webcam analysis
- **Adaptive Recommendations**: AI-driven learning suggestions

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /profile` - Get user profile
- `POST /update_password` - Change password

### Study Tools
- `POST /upload_note` - Upload study material
- `POST /extract_text` - Extract text from material
- `POST /generate_summary` - Generate AI summary
- `POST /generate_mcq` - Generate MCQs
- `POST /generate_flashcards` - Generate flashcards
- `POST /explain` - Get AI explanation
- `GET /materials` - List user's materials
- `GET /ai_outputs` - List generated content

### Progress & Analytics
- `POST /save_progress` - Update material progress
- `GET /get_progress` - Get progress data

### Cognitive Features
- `POST /analyze_eye_metrics` - Process eye-tracking data
- `POST /analyze_emotion` - Detect facial emotions
- `POST /get_cognitive_load` - Calculate cognitive load
- `POST /store_cognitive_data` - Save session metrics
- `GET /cognitive_data` - Retrieve cognitive history

### Admin/Teacher
- `GET /all_users` - List all users (admin)
- `POST /approve_teacher` - Approve teacher role (admin)
- `POST /delete_user` - Remove user (admin)
- `GET /system_logs` - View audit logs (admin)
- `GET /teacher/progress` - View student progress (teacher/admin)

## Configuration

### Environment Variables
- `SMART_STUDY_SECRET`: JWT secret key (defaults to 'change_me_secret')
- `API_BASE_URL`: Backend URL for frontend (defaults to http://localhost:5000)

### File Upload Settings
- Supported formats: PDF, TXT, PNG, JPG, JPEG
- Max file size: Limited by Flask defaults (can be configured)
- Upload directory: `smart_study_app/images/uploads/`

## Development

### Project Structure
```
smart_study_app/
├── api/
│   ├── cognitive/          # Eye-tracking & emotion analysis
│   ├── routes/             # Flask blueprints
│   ├── adaptive_engine.py  # Recommendation logic
│   ├── authentication.py   # Auth utilities
│   ├── database.py         # DB setup & helpers
│   └── app.py              # Flask application
├── frontend/
│   ├── components/         # Reusable UI components
│   ├── *.py                # Streamlit pages
│   └── ...
├── images/                 # Static assets
├── requirements.txt        # Python dependencies
├── smartstudy.db           # SQLite database
└── app.py                  # Main Streamlit app
```

### Adding New Features
1. **Backend**: Add routes in appropriate blueprint, update database if needed
2. **Frontend**: Create new page file, add to app.py routing
3. **Components**: Place reusable widgets in `components/`
4. **Dependencies**: Update requirements.txt for new packages

## Security Notes
- Passwords hashed with SHA256 (consider upgrading to bcrypt)
- JWT tokens expire in 24 hours
- File uploads validated for type and size
- Role-based API access control
- Webcam data processed locally (no external transmission)

## Troubleshooting

### Common Issues
- **Camera not working**: Ensure browser permissions for WebRTC
- **AI generation fails**: Check AI model integration (currently placeholders)
- **Upload errors**: Verify file format and Flask upload settings
- **Database errors**: Run `python api/database.py` to initialize tables

### Logs
- Flask logs: Console output from `python api/app.py`
- Streamlit logs: Console output from `streamlit run app.py`
- System logs: Available in admin panel

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with proper testing
4. Submit a pull request

## License

This project is for educational purposes. Check individual library licenses for commercial use.
