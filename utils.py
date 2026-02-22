import re
import cv2
import numpy as np
from typing import Tuple
import PyPDF2
from io import BytesIO
import base64

def calculate_cognitive_load(gaze_score: float, student_cognitive_limit: int) -> Tuple[float, str]:
    """
    Calculate cognitive load and emotional state based on gaze score and student's cognitive limit
    
    Args:
        gaze_score: 0 to 1 (1 = perfect gaze tracking, 0 = poor tracking)
        student_cognitive_limit: student's cognitive limit threshold (typically 50-80)
    
    Returns:
        Tuple of (cognitive_load, emotional_state)
    """
    # Base cognitive load from gaze score (inverted: poor gaze = higher load)
    base_load = (1 - gaze_score) * 60  # 0-60% base load
    
    # Add some variability and realistic factors
    # Add random variation to simulate natural cognitive fluctuations
    import random
    variation = random.uniform(-10, 15)  # ±10-15% variation
    
    # Consider student's cognitive limit - adjust load accordingly
    if student_cognitive_limit > 70:  # High cognitive limit student
        limit_factor = 0.8  # Can handle more load
    elif student_cognitive_limit > 50:  # Average student
        limit_factor = 1.0  # Normal load
    else:  # Lower cognitive limit student
        limit_factor = 1.2  # More affected by load
    
    # Calculate final cognitive load
    cognitive_load = max(15, min(95, (base_load + variation) * limit_factor))  # Clamp between 15-95%
    
    # Emotional state based on cognitive load vs student's limit
    if cognitive_load > student_cognitive_limit * 1.2:
        emotional_state = "overwhelmed"
    elif cognitive_load > student_cognitive_limit:
        emotional_state = "stressed"
    elif cognitive_load > student_cognitive_limit * 0.6:
        emotional_state = "focused"
    elif cognitive_load > student_cognitive_limit * 0.3:
        emotional_state = "relaxed"
    else:
        emotional_state = "bored"
    
    return cognitive_load, emotional_state

def calculate_engagement(face_attention_score: float) -> float:
    """
    Calculate engagement level based on face attention score with realistic variations
    
    Args:
        face_attention_score: 0 to 1 (1 = full attention, 0 = no attention)
    
    Returns:
        Engagement percentage (0 to 100)
    """
    import random
    
    # Base engagement from face attention
    base_engagement = face_attention_score * 80  # Max 80% base from attention
    
    # Add realistic variation (attention fluctuates naturally)
    variation = random.uniform(-15, 20)  # ±15-20% variation
    
    # Add some baseline engagement (even with poor attention, there's some engagement)
    baseline = random.uniform(5, 15)  # 5-15% baseline
    
    # Calculate final engagement
    engagement = max(10, min(95, base_engagement + variation + baseline))
    
    return engagement

def simple_text_summarizer(text: str, max_sentences: int = 3) -> str:
    """
    Simple text summarizer using extractive approach
    
    Args:
        text: Input text to summarize
        max_sentences: Maximum number of sentences in summary
    
    Returns:
        Summarized text
    """
    if not text or len(text.strip()) < 50:
        return text
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= max_sentences:
        return '. '.join(sentences)
    
    # Simple scoring: longer sentences and those with important keywords
    important_words = ['important', 'key', 'main', 'primary', 'essential', 'crucial', 'significant']
    
    scored_sentences = []
    for i, sentence in enumerate(sentences):
        score = len(sentence)  # Longer sentences get higher scores
        
        # Bonus for important keywords
        for word in important_words:
            if word.lower() in sentence.lower():
                score += 20
        
        # Position bonus (first and last sentences are often important)
        if i == 0 or i == len(sentences) - 1:
            score += 10
            
        scored_sentences.append((score, sentence))
    
    # Sort by score and take top sentences
    scored_sentences.sort(reverse=True)
    top_sentences = [sent[1] for sent in scored_sentences[:max_sentences]]
    
    # Reorder based on original position
    final_summary = []
    for sentence in sentences:
        if sentence in top_sentences and len(final_summary) < max_sentences:
            final_summary.append(sentence)
    
    return '. '.join(final_summary) + '.'

def extract_text_from_pdf(pdf_content: bytes) -> str:
    """
    Extract text from PDF file
    
    Args:
        pdf_content: PDF file content as bytes
    
    Returns:
        Extracted text
    """
    try:
        pdf_file = BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        return f"Error extracting PDF text: {str(e)}"

def extract_text_from_txt(txt_content: bytes) -> str:
    """
    Extract text from TXT file
    
    Args:
        txt_content: TXT file content as bytes
    
    Returns:
        Extracted text
    """
    try:
        return txt_content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            return txt_content.decode('latin-1')
        except Exception as e:
            return f"Error decoding text file: {str(e)}"

def get_cognitive_load_level(cognitive_load: float) -> str:
    """
    Get cognitive load level category
    
    Args:
        cognitive_load: Cognitive load percentage (0-100)
    
    Returns:
        Level category (low, medium, high, critical)
    """
    if cognitive_load < 30:
        return "low"
    elif cognitive_load < 60:
        return "medium"
    elif cognitive_load < 80:
        return "high"
    else:
        return "critical"

def get_recommended_next_course(student_id: int, current_course_id: int) -> int:
    """
    Get next recommended course for student
    
    Args:
        student_id: Student ID
        current_course_id: Current course ID
    
    Returns:
        Next course ID (or current_course_id + 1 if available)
    """
    # Simple recommendation: next course in sequence
    # In a real app, this would be more sophisticated
    return current_course_id + 1 if current_course_id else 1

def analyze_face_from_image(image_data: str) -> Tuple[float, float, bool]:
    """
    Analyze face from base64 image data to extract gaze and attention metrics
    
    Args:
        image_data: Base64 encoded image string
    
    Returns:
        Tuple of (gaze_score, face_attention_score, face_detected)
    """
    try:
        # Decode base64 image
        image_data = image_data.split(',')[1] if ',' in image_data else image_data
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return 0.0, 0.0, False  # No scores when no image
        
        # Load face cascade classifier
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return 0.0, 0.0, False  # No scores when no face detected
        
        # Get the largest face
        face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = face
        
        # Extract face region
        face_region = gray[y:y+h, x:x+w]
        
        # Detect eyes in face region
        eyes = eye_cascade.detectMultiScale(face_region, 1.1, 3)
        
        # Initialize scores with realistic defaults
        gaze_score = 0.4  # Default moderate gaze
        face_attention_score = 0.5  # Default moderate attention
        
        if len(eyes) >= 2:
            # Eyes detected - calculate gaze based on eye position and size
            eye_areas = [eye[2] * eye[3] for eye in eyes]
            avg_eye_area = np.mean(eye_areas)
            face_area = w * h
            
            # More realistic gaze score calculation
            eye_to_face_ratio = avg_eye_area / face_area if face_area > 0 else 0
            
            # Base gaze score on eye detection quality (not just size)
            # Typical eye-to-face ratio is around 0.01-0.03
            if 0.01 <= eye_to_face_ratio <= 0.05:
                gaze_score = 0.8  # Good eye detection
            elif 0.005 <= eye_to_face_ratio < 0.01 or 0.05 < eye_to_face_ratio <= 0.1:
                gaze_score = 0.6  # Moderate eye detection
            else:
                gaze_score = 0.3  # Poor eye detection
            
            # Face attention based on face size and position
            img_center_x = img.shape[1] / 2
            face_center_x = x + w / 2
            
            # Center alignment score (closer to center = higher attention)
            center_distance = abs(face_center_x - img_center_x)
            max_distance = img.shape[1] / 2
            center_score = max(0, 1 - (center_distance / max_distance))
            
            # Size score (not too small, not too large)
            face_ratio = (w * h) / (img.shape[0] * img.shape[1])
            if 0.02 <= face_ratio <= 0.15:  # Good face size
                size_score = 1.0
            elif 0.01 <= face_ratio < 0.02 or 0.15 < face_ratio <= 0.25:
                size_score = 0.7
            else:
                size_score = 0.4
            
            face_attention_score = (center_score * 0.6 + size_score * 0.4)
        
        # Enhanced eye openness detection
        if len(eyes) >= 2:
            total_eye_openness = 0
            valid_eyes = 0
            
            for (ex, ey, ew, eh) in eyes[:2]:  # Take first 2 eyes
                if ex >= 0 and ey >= 0 and ex + ew <= face_region.shape[1] and ey + eh <= face_region.shape[0]:
                    eye_roi = face_region[ey:ey+eh, ex:ex+ew]
                    
                    # Enhanced eye openness detection using multiple methods
                    # Method 1: Brightness analysis (white pixels in eye area)
                    _, thresh = cv2.threshold(eye_roi, 80, 255, cv2.THRESH_BINARY)
                    white_pixels = np.sum(thresh == 255)
                    total_pixels = eye_roi.size
                    brightness_openness = white_pixels / total_pixels if total_pixels > 0 else 0
                    
                    # Method 2: Variance analysis (open eyes have more variance)
                    variance = np.var(eye_roi)
                    variance_openness = min(1.0, variance / 1000)  # Normalize variance
                    
                    # Method 3: Edge detection (open eyes have more edges)
                    edges = cv2.Canny(eye_roi, 50, 150)
                    edge_pixels = np.sum(edges > 0)
                    edge_openness = min(1.0, edge_pixels / (eye_roi.size * 0.1))
                    
                    # Combine methods for more robust detection
                    combined_openness = (brightness_openness * 0.4 + variance_openness * 0.3 + edge_openness * 0.3)
                    
                    # If eye is likely closed (low openness), reduce gaze score significantly
                    if combined_openness < 0.15:  # Likely closed eyes
                        gaze_score *= 0.3  # Major reduction for closed eyes
                    elif combined_openness < 0.25:  # Partially closed/squinting
                        gaze_score *= 0.6  # Moderate reduction
                    # If eyes are open, slightly increase gaze score
                    elif combined_openness > 0.4:
                        gaze_score = min(1.0, gaze_score * 1.1)
                    
                    total_eye_openness += combined_openness
                    valid_eyes += 1
            
            # Average eye openness for debugging
            avg_openness = total_eye_openness / valid_eyes if valid_eyes > 0 else 0
            print(f"Eye openness: {avg_openness:.3f}, Adjusted gaze: {gaze_score:.3f}")
        
        else:
            # No eyes detected - return 0 scores
            return 0.0, 0.0, True
        
        # Add some realistic variation and ensure values are in valid range
        gaze_score = max(0.1, min(1.0, gaze_score))
        face_attention_score = max(0.2, min(1.0, face_attention_score))
        
        # Add small random variation to make it more realistic (±5%)
        import random
        gaze_score += random.uniform(-0.05, 0.05)
        face_attention_score += random.uniform(-0.05, 0.05)
        
        # Final clamp to ensure valid range
        gaze_score = max(0.0, min(1.0, gaze_score))
        face_attention_score = max(0.0, min(1.0, face_attention_score))
        
        return gaze_score, face_attention_score, True
        
    except Exception as e:
        print(f"Error analyzing face: {str(e)}")
        return 0.0, 0.0, False  # No scores on error

def detect_emotional_state(face_image_data: str) -> str:
    """
    Detect emotional state from face image (simplified)
    
    Args:
        face_image_data: Base64 encoded face image
    
    Returns:
        Emotional state (stress, normal, relaxed)
    """
    try:
        # Decode image
        image_data = face_image_data.split(',')[1] if ',' in face_image_data else face_image_data
        image_bytes = base64.b64decode(image_data)
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return "normal"
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Simple emotion detection based on facial feature analysis
        # This is a simplified version - real emotion detection would use ML models
        
        # Detect face
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return "normal"
        
        # Get the largest face
        face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = face
        
        # Extract face region
        face_region = gray[y:y+h, x:x+w]
        
        # Simple analysis: check for mouth curvature and eye openness
        # Upper third of face (eyes area)
        eye_region = face_region[:int(h*0.4), :]
        # Lower third of face (mouth area)
        mouth_region = face_region[int(h*0.6):, :]
        
        # Calculate variance in these regions (simplified emotion indicator)
        eye_variance = np.var(eye_region)
        mouth_variance = np.var(mouth_region)
        
        # Very simplified emotion classification
        if eye_variance < 100 and mouth_variance < 200:
            return "relaxed"
        elif eye_variance > 500 or mouth_variance > 800:
            return "stress"
        else:
            return "normal"
            
    except Exception as e:
        print(f"Error detecting emotion: {str(e)}")
        return "normal"
