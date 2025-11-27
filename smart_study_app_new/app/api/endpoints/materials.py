import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import shutil
from datetime import datetime

from ... import models, schemas, auth
from ...database import get_db
from ...config import settings

router = APIRouter(prefix="/materials", tags=["study_materials"])

def save_upload_file(upload_file: UploadFile, user_id: int) -> str:
    """Save uploaded file to the uploads directory and return the file path."""
    # Create uploads directory if it doesn't exist
    user_upload_dir = os.path.join(settings.UPLOAD_FOLDER, str(user_id))
    os.makedirs(user_upload_dir, exist_ok=True)
    
    # Create a unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_ext = os.path.splitext(upload_file.filename)[1]
    filename = f"{timestamp}{file_ext}"
    file_path = os.path.join(user_upload_dir, filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return file_path

def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()

@router.post("/upload/", response_model=schemas.StudyMaterial)
async def upload_material(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    subject: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Check file extension
    file_ext = get_file_extension(file.filename)
    if file_ext[1:] not in settings.ALLOWED_EXTENSIONS:  # Remove the dot
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    try:
        # Save the file
        file_path = save_upload_file(file, current_user.id)
        
        # Create material record in database
        db_material = models.StudyMaterial(
            title=title,
            description=description,
            subject=subject,
            tags=tags,
            file_path=file_path,
            owner_id=current_user.id
        )
        
        db.add(db_material)
        db.commit()
        db.refresh(db_material)
        
        return db_material
        
    except Exception as e:
        # Clean up the file if something went wrong
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading file: {str(e)}"
        )

@router.get("/", response_model=List[schemas.StudyMaterial])
def list_materials(
    skip: int = 0, 
    limit: int = 100,
    subject: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    query = db.query(models.StudyMaterial)
    
    # Filter by owner (users can only see their own materials unless they're admin/teacher)
    if current_user.role == "student":
        query = query.filter(models.StudyMaterial.owner_id == current_user.id)
    
    # Apply filters
    if subject:
        query = query.filter(models.StudyMaterial.subject == subject)
    if tag:
        query = query.filter(models.StudyMaterial.tags.contains(tag))
    
    return query.offset(skip).limit(limit).all()

@router.get("/{material_id}", response_model=schemas.StudyMaterial)
def get_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    material = db.query(models.StudyMaterial).filter(models.StudyMaterial.id == material_id).first()
    
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Check permissions
    if current_user.role == "student" and material.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this material"
        )
    
    return material

@router.put("/{material_id}", response_model=schemas.StudyMaterial)
def update_material(
    material_id: int,
    material_update: schemas.StudyMaterialUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_material = db.query(models.StudyMaterial).filter(models.StudyMaterial.id == material_id).first()
    
    if not db_material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Check permissions
    if current_user.role == "student" and db_material.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to update this material"
        )
    
    # Update fields
    if material_update.title is not None:
        db_material.title = material_update.title
    if material_update.description is not None:
        db_material.description = material_update.description
    if material_update.subject is not None:
        db_material.subject = material_update.subject
    if material_update.tags is not None:
        db_material.tags = material_update.tags
    
    db.commit()
    db.refresh(db_material)
    
    return db_material

@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    db_material = db.query(models.StudyMaterial).filter(models.StudyMaterial.id == material_id).first()
    
    if not db_material:
        raise HTTPException(status_code=404, detail="Material not found")
    
    # Check permissions
    if current_user.role == "student" and db_material.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this material"
        )
    
    # Delete the file
    if os.path.exists(db_material.file_path):
        try:
            os.remove(db_material.file_path)
        except Exception as e:
            # Log the error but continue with database deletion
            pass
    
    # Delete the record
    db.delete(db_material)
    db.commit()
    
    return {"ok": True}
