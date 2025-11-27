Below is the complete modular expansion to add the missing features:

✅ 1. Add New Folder: cognitive_engine inside /api
api/
  └── cognitive/
        ├── eye_tracking.py
        ├── emotional_analysis.py
        ├── cognitive_load.py
        ├── webcam_stream.py

✅ Purpose

Adds support for:

Eye tracking

Emotional recognition

Pupil dilation + gaze dispersion

Blink rate

Cognitive load calculation

✅ Functions

eye_tracking.py

detect_gaze_direction(frame)
measure_blink_rate(frame)
detect_pupil_dilation(frame)


emotional_analysis.py

predict_emotion(frame)


cognitive_load.py

compute_cognitive_load(eye_metrics, emotional_state)
return cognitive_load_score


webcam_stream.py

capture_real_time_feed()
return frame


✅ This aligns with the IEEE papers in your PPT.

✅ 2. New API Routes (Add Without Touching Existing Ones)

Add inside:

api/routes/cognitive_routes.py

✅ Endpoints
Endpoint	Function
/capture_frame	Captures webcam frame
/analyze_eye_metrics	Processes gaze, blink, pupil dilation
/get_cognitive_load	Returns cognitive load score
/store_cognitive_data	Saves session-based cognitive data
✅ Purpose

Keeps AI features separate and modular.

✅ 3. Update Database With New Tables
New Table 1: cognitive_data

Stores eye-tracking & emotional data.

| id | user_id | blink_rate | gaze_variance | pupil_size | emotion | load_score | timestamp |

New Table 2: learning_state

Tracks adaptive adjustments.

| id | user_id | material_id | difficulty_level | recommended_next_task | timestamp |

✅ No changes to existing DB tables.
✅ Fully backward-compatible.

✅ 4. Add New Adaptive Engine Layer

Add file:

api/adaptive_engine.py

✅ Purpose

Combines:

Cognitive load score

Emotion

Study performance

Time spent

Content difficulty

✅ Outputs

Recommend content difficulty

Show "focus score"

Suggest break time

Suggest revision topics

✅ Function Example
get_recommendation(cognitive_score, progress_score):
    if cognitive_score > 0.7:
        return "Take a short break or switch to light content"
    if progress_score < 0.4:
        return "Revise previous chapter"
    return "Proceed to next level"

✅ 5. Frontend Add-On Pages (Streamlit)

Add 3 new pages in /frontend:

frontend/
  ├── cognitive_dashboard.py
  ├── attention_meter.py
  └── adaptive_recommendations.py

✅ 1. cognitive_dashboard.py

Shows:

Cognitive load graph

Focus vs distraction timeline

Eye-tracking stats

Emotion timeline

✅ 2. attention_meter.py

Real-time feed:

WebCam window

Live focus score

Live cognitive load score

✅ 3. adaptive_recommendations.py

Shows AI-driven suggestions:

Next best topic

Difficulty adjustments

Revision suggestions

Personalized learning path

✅ No modification to existing UI pages.

✅ 6. Add UI Elements (Reusable Components)

Add inside:

frontend/components/
  ├── cognitive_widgets.py
  └── adaptive_cards.py

✅ Widgets include:

Cognitive load gauge meter

Emotion radar graph

Attention timeline

Adaptive recommendation box

✅ Plug-and-play in any Streamlit page.

✅ 7. Add Adaptive Flow to Existing Features
✅ Whenever user:

Generates MCQ

Views summary

Uses flashcards

Track:

Time spent

Difficulty properly answered

Cognitive load score

Then store in learning_state.

✅ Recommendation Examples:

If cognitive load high → Suggest easy MCQs

If emotional stress detected → Suggest break

If user is consistently correct → Increase difficulty

This DOES NOT break existing features.

✅ 8. Workflow Integration Map (Add-on Layer Only)
✅ 1. User opens study material

↓
webcam feed starts (optional toggle)
↓
collect eye + emotional metrics
↓
compute cognitive load
↓
store cognitive metrics in DB

✅ 2. User starts learning / generating MCQ

↓
adaptive_engine checks:

cognitive score

past performance

difficulty level
↓
generates:

personalized difficulty

personalized recommendations

✅ 3. User views Cognition Dashboard

Shows:

Heatmaps

Focus score

Emotional changes

Difficulty pattern