from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import os
import PyPDF2
from typing import List, Dict, Any
from ... import schemas, models, auth
from ...database import get_db
from ...services.ai_service import ai_service
import json

router = APIRouter(prefix="/ai", tags=["ai_processing"])

def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error extracting text from PDF: {str(e)}"
        )

@router.post("/summarize", response_model=schemas.AISummaryResponse)
async def summarize_text(
    request: schemas.AISummarizeRequest,
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Generate a summary of the provided text using Gemini."""
    try:
        summary = await ai_service.generate_summary(request.text)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-flashcards", response_model=schemas.AIGenerateFlashcardsResponse)
async def generate_flashcards(
    request: schemas.AIGenerateFlashcardsRequest,
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Generate flashcards from the provided text using Gemini."""
    try:
        flashcards = await ai_service.generate_flashcards(
            text=request.text,
            num_cards=request.num_cards
        )
        return {"flashcards": flashcards}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-mcq", response_model=schemas.AIGenerateMCQResponse)
async def generate_mcq_questions(
    request: schemas.AIGenerateMCQRequest,
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Generate multiple-choice questions from the provided text."""
    prompt = f"""
    Generate {request.num_questions} multiple-choice questions based on the following text.
    Each question should have 4 options with one correct answer.
    Format each question as:
    Q: [question]
    A) [option 1]
    B) [option 2]
    C) [option 3]
    D) [option 4]
    Answer: [correct option letter]
    
    Text to create questions from:
    {request.text}
    """
    
    response = await ai_service.generate_mcq_questions(prompt, max_tokens=1500)
    
    # Parse the response into MCQ questions
    questions = []
    current_question = None
    
    for line in response.split('\n'):
        line = line.strip()
        if line.startswith('Q:'):
            if current_question:
                questions.append(current_question)
            current_question = {"question": line[2:].strip(), "options": []}
        elif line and line[0] in 'ABCD)' and 'Answer:' not in line:
            option_text = line.split(')', 1)[1].strip()
            current_question["options"].append({
                "text": option_text,
                "is_correct": False
            })
        elif line.startswith('Answer:'):
            correct_option = line.split(':', 1)[1].strip().upper()
            if current_question and correct_option in 'ABCD':
                idx = ord(correct_option) - ord('A')
                if 0 <= idx < len(current_question["options"]):
                    current_question["options"][idx]["is_correct"] = True
    
    if current_question:
        questions.append(current_question)
    
    return {"questions": questions[:request.num_questions]}

@router.post("/explain", response_model=schemas.AIExplainResponse)
async def explain_concept(
    request: schemas.AIExplainRequest,
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Explain a concept in simple terms using Gemini."""
    try:
        explanation = await ai_service.generate_explanation(
            text=request.context if request.context else "No additional context provided.",
            concept=request.concept
        )
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-material/{material_id}")
async def process_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Process a study material to extract text and generate summaries, flashcards, and MCQs."""
    # Get the material
    material = db.query(models.StudyMaterial).filter(
        models.StudyMaterial.id == material_id,
        models.StudyMaterial.owner_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(status_code=404, detail="Material not found or access denied")
    
    # Check if the file exists
    if not os.path.exists(material.file_path):
        raise HTTPException(status_code=404, detail="Material file not found")
    
    # Extract text based on file type
    file_ext = os.path.splitext(material.file_path)[1].lower()
    
    if file_ext == '.pdf':
        text = extract_text_from_pdf(material.file_path)
    elif file_ext == '.txt':
        with open(material.file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    # Generate summaries, flashcards, and MCQs
    summary_prompt = f"Please provide a concise summary of the following text in 200 words or less:\n\n{text[:8000]}"  # Limit text length
    summary = generate_ai_response(summary_prompt, max_tokens=300)
    
    # Update material with extracted text and summary
    # Note: In a production app, you might want to store this in a separate table
    
    return {
        "material_id": material.id,
        "summary": summary,
        "text_extract": text[:1000] + "..." if len(text) > 1000 else text,
        "suggested_flashcards": await generate_flashcards(
            schemas.AIGenerateFlashcardsRequest(text=text[:4000], num_cards=5)
        ),
        "suggested_questions": await generate_mcq_questions(
            schemas.AIGenerateMCQRequest(text=text[:4000], num_questions=3)
        )
    }
