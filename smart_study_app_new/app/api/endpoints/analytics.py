from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional

from ... import models, schemas, auth
from ...database import get_db

router = APIRouter(prefix="/analytics", tags=["analytics"])

def get_study_time_stats(user_id: int, db: Session, days: int = 30):
    """Get study time statistics for a user."""
    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Query for total study time
    total_time = db.query(
        func.sum(models.StudySession.duration_minutes).label("total_minutes")
    ).filter(
        models.StudySession.user_id == user_id,
        models.StudySession.start_time >= start_date,
        models.StudySession.end_time.isnot(None)
    ).scalar() or 0
    
    # Query for daily study time
    daily_stats = db.query(
        func.date(models.StudySession.start_time).label("study_date"),
        func.sum(models.StudySession.duration_minutes).label("total_minutes")
    ).filter(
        models.StudySession.user_id == user_id,
        models.StudySession.start_time >= start_date,
        models.StudySession.end_time.isnot(None)
    ).group_by(
        func.date(models.StudySession.start_time)
    ).all()
    
    # Format daily stats
    daily_data = [
        {"date": str(stat.study_date), "minutes": int(stat.total_minutes or 0)}
        for stat in daily_stats
    ]
    
    return {
        "total_minutes": int(total_time),
        "daily_data": daily_data
    }

def get_subject_breakdown(user_id: int, db: Session):
    """Get study time breakdown by subject."""
    # Query for study time by subject
    subject_stats = db.query(
        models.StudyMaterial.subject,
        func.sum(models.StudySession.duration_minutes).label("total_minutes")
    ).join(
        models.StudyMaterial,
        models.StudySession.material_id == models.StudyMaterial.id
    ).filter(
        models.StudySession.user_id == user_id,
        models.StudySession.end_time.isnot(None),
        models.StudyMaterial.subject.isnot(None)
    ).group_by(
        models.StudyMaterial.subject
    ).all()
    
    return [
        {"subject": stat.subject, "minutes": int(stat.total_minutes or 0)}
        for stat in subject_stats
    ]

def get_streak_data(user_id: int, db: Session):
    """Calculate the user's current study streak."""
    # Get all unique study days
    study_days = db.query(
        func.date(models.StudySession.start_time).label("study_date")
    ).filter(
        models.StudySession.user_id == user_id,
        models.StudySession.end_time.isnot(None)
    ).distinct().order_by(
        func.date(models.StudySession.start_time).desc()
    ).all()
    
    # Calculate streak
    streak = 0
    today = datetime.utcnow().date()
    prev_day = today
    
    for day in study_days:
        day_date = day.study_date
        
        # If we're checking today or yesterday, continue the streak
        if day_date == today or day_date == today - timedelta(days=1):
            streak += 1
            today = day_date
        # If there's a gap of more than one day, break the streak
        elif (prev_day - day_date).days > 1:
            break
        else:
            streak += 1
        
        prev_day = day_date
    
    return {"current_streak": streak}

@router.get("/user/{user_id}", response_model=schemas.UserAnalyticsResponse)
def get_user_analytics(
    user_id: int,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get analytics for a specific user."""
    # Check permissions
    if current_user.role == "student" and current_user.id != user_id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to view analytics for this user"
        )
    
    # Get study time statistics
    time_stats = get_study_time_stats(user_id, db, days)
    
    # Get subject breakdown
    subject_breakdown = get_subject_breakdown(user_id, db)
    
    # Get streak data
    streak_data = get_streak_data(user_id, db)
    
    # Get recent materials
    recent_materials = db.query(
        models.StudyMaterial,
        func.count(models.StudySession.id).label("session_count"),
        func.sum(models.StudySession.duration_minutes).label("total_time")
    ).join(
        models.StudySession,
        models.StudySession.material_id == models.StudyMaterial.id
    ).filter(
        models.StudySession.user_id == user_id,
        models.StudySession.end_time.isnot(None)
    ).group_by(
        models.StudyMaterial.id
    ).order_by(
        func.max(models.StudySession.start_time).desc()
    ).limit(5).all()
    
    # Format recent materials
    recent_materials_data = [
        {
            "material_id": mat.id,
            "title": mat.title,
            "subject": mat.subject,
            "session_count": session_count,
            "total_time": int(total_time or 0)
        }
        for mat, session_count, total_time in recent_materials
    ]
    
    # Calculate overall stats
    total_materials = db.query(models.StudyMaterial).filter(
        models.StudyMaterial.owner_id == user_id
    ).count()
    
    total_sessions = db.query(models.StudySession).filter(
        models.StudySession.user_id == user_id,
        models.StudySession.end_time.isnot(None)
    ).count()
    
    # Calculate average score (placeholder - would come from quizzes/exercises)
    average_score = None
    
    return {
        "user_id": user_id,
        "overall": {
            "total_study_time": time_stats["total_minutes"],
            "materials_studied": total_materials,
            "total_sessions": total_sessions,
            "average_score": average_score,
            "current_streak": streak_data["current_streak"]
        },
        "time_series": time_stats["daily_data"],
        "by_subject": subject_breakdown,
        "recent_materials": recent_materials_data
    }

@router.get("/materials/{material_id}")
def get_material_analytics(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Get analytics for a specific study material."""
    # Check if user has access to this material
    material = db.query(models.StudyMaterial).filter(
        models.StudyMaterial.id == material_id,
        models.StudyMaterial.owner_id == current_user.id
    ).first()
    
    if not material:
        raise HTTPException(
            status_code=404,
            detail="Material not found or access denied"
        )
    
    # Get study sessions for this material
    sessions = db.query(models.StudySession).filter(
        models.StudySession.material_id == material_id,
        models.StudySession.end_time.isnot(None)
    ).all()
    
    # Calculate total time spent
    total_time = sum(session.duration_minutes or 0 for session in sessions)
    
    # Get unique users (for teachers/admins)
    unique_users = db.query(models.User).join(
        models.StudySession,
        models.StudySession.user_id == models.User.id
    ).filter(
        models.StudySession.material_id == material_id
    ).distinct().count()
    
    # Get session history
    session_history = [
        {
            "session_id": session.id,
            "user_id": session.user_id,
            "start_time": session.start_time,
            "duration_minutes": session.duration_minutes,
            "end_time": session.end_time
        }
        for session in sessions
    ]
    
    return {
        "material_id": material.id,
        "title": material.title,
        "total_study_time": total_time,
        "total_sessions": len(sessions),
        "unique_users": unique_users,
        "sessions": session_history
    }
