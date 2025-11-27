from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from ... import models, schemas, auth
from ...database import get_db

router = APIRouter(prefix="/study-sessions", tags=["study_sessions"])

@router.post("/start", response_model=schemas.StudySession)
def start_study_session(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Start a new study session for the given material."""
    # Check if material exists and user has access
    material = db.query(models.StudyMaterial).filter(
        models.StudyMaterial.id == material_id,
        models.StudyMaterial.owner_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found or access denied"
        )
    
    # Check for existing active session
    active_session = db.query(models.StudySession).filter(
        models.StudySession.user_id == current_user.id,
        models.StudySession.end_time.is_(None)
    ).first()
    
    if active_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active study session. Please end it before starting a new one."
        )
    
    # Create new session
    db_session = models.StudySession(
        user_id=current_user.id,
        material_id=material_id,
        start_time=datetime.utcnow()
    )
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return db_session

@router.post("/{session_id}/end", response_model=schemas.StudySession)
def end_study_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """End an active study session."""
    # Get the session
    db_session = db.query(models.StudySession).filter(
        models.StudySession.id == session_id,
        models.StudySession.user_id == current_user.id
    ).first()
    
    if not db_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or access denied"
        )
    
    if db_session.end_time is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This session has already ended"
        )
    
    # Calculate duration in minutes
    end_time = datetime.utcnow()
    duration = int((end_time - db_session.start_time).total_seconds() / 60)
    
    # Update session
    db_session.end_time = end_time
    db_session.duration_minutes = duration
    
    db.commit()
    db.refresh(db_session)
    
    return db_session

@router.get("/", response_model=List[schemas.StudySession])
def list_study_sessions(
    skip: int = 0,
    limit: int = 100,
    material_id: Optional[int] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """List study sessions with optional filtering."""
    query = db.query(models.StudySession)
    
    # Regular users can only see their own sessions
    if current_user.role == "student":
        query = query.filter(models.StudySession.user_id == current_user.id)
    # Teachers can see sessions for their students
    elif current_user.role == "teacher" and user_id is None:
        # This would need to be implemented based on your teacher-student relationship
        pass
    # Admins can see all sessions
    
    # Apply filters
    if material_id is not None:
        query = query.filter(models.StudySession.material_id == material_id)
    if user_id is not None and (current_user.role in ["admin", "teacher"] or user_id == current_user.id):
        query = query.filter(models.StudySession.user_id == user_id)
    
    return query.offset(skip).limit(limit).all()

@router.get("/{session_id}", response_model=schemas.StudySession)
def get_study_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get details of a specific study session."""
    query = db.query(models.StudySession)
    
    # Regular users can only see their own sessions
    if current_user.role == "student":
        query = query.filter(models.StudySession.user_id == current_user.id)
    
    session = query.filter(models.StudySession.id == session_id).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or access denied"
        )
    
    return session
