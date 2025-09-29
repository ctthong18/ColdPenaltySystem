from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
import uuid

from app.api import deps
from app.crud import violation as crud_violation, camera as crud_camera
from app.schemas.violation import Violation, ViolationUpdate
from app.models.user import User
from app.core.config import settings

router = APIRouter()

@router.get("/assigned-violations", response_model=List[Violation])
def get_assigned_violations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query("pending"),
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Get violations assigned to current officer or pending violations.
    """
    violations = crud_violation.get_violations(
        db, 
        skip=skip, 
        limit=limit,
        status=status
    )
    return violations

@router.get("/my-processed-violations", response_model=List[Violation])
def get_my_processed_violations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Get violations processed by current officer in the last N days.
    """
    date_from = datetime.utcnow() - timedelta(days=days)
    
    # In a real implementation, you'd filter by processed_by = current_user.id
    violations = crud_violation.get_violations(
        db, 
        skip=skip, 
        limit=limit,
        status="processed",
        date_from=date_from
    )
    return violations

@router.put("/process-violation/{violation_id}", response_model=Violation)
def process_violation(
    *,
    db: Session = Depends(deps.get_db),
    violation_id: int,
    violation_update: ViolationUpdate,
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Process a violation (approve, reject, or modify).
    """
    violation = crud_violation.get_violation(db, violation_id=violation_id)
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")
    
    if violation.status != "pending":
        raise HTTPException(
            status_code=400, 
            detail="Only pending violations can be processed"
        )
    
    # Set status to processed if not specified
    if not violation_update.status:
        violation_update.status = "processed"
    
    violation = crud_violation.update_violation(
        db, 
        violation_id=violation_id, 
        violation_update=violation_update,
        processed_by=current_user.id
    )
    return violation

@router.post("/upload-evidence/{violation_id}")
async def upload_evidence(
    *,
    violation_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Upload additional evidence for a violation.
    """
    violation = crud_violation.get_violation(db, violation_id=violation_id)
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")
    
    uploaded_files = []
    
    for file in files:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "video/mp4", "video/avi"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} not allowed"
            )
        
        # Generate unique filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
        
        # Save file
        os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            if len(content) > settings.MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail="File too large"
                )
            buffer.write(content)
        
        uploaded_files.append(f"/uploads/{unique_filename}")
    
    return {
        "message": f"Uploaded {len(uploaded_files)} files successfully",
        "files": uploaded_files
    }

@router.get("/workload-statistics")
def get_workload_statistics(
    db: Session = Depends(deps.get_db),
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Get officer's workload statistics.
    """
    date_from = datetime.utcnow() - timedelta(days=days)
    
    # In a real implementation, these would be filtered by current_user.id
    total_assigned = crud_violation.get_violations(
        db, status="pending", limit=1000
    )
    
    total_processed = crud_violation.get_violations(
        db, status="processed", date_from=date_from, limit=1000
    )
    
    return {
        "pending_violations": len(total_assigned),
        "processed_violations": len(total_processed),
        "processing_rate": len(total_processed) / max(len(total_assigned) + len(total_processed), 1) * 100,
        "period_days": days,
        "officer_name": current_user.full_name,
        "badge_number": current_user.badge_number
    }

@router.get("/recent-activity", response_model=List[Violation])
def get_recent_activity(
    db: Session = Depends(deps.get_db),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Get officer's recent activity (last processed violations).
    """
    # In a real implementation, this would filter by processed_by = current_user.id
    violations = crud_violation.get_violations(
        db, 
        limit=limit,
        status="processed"
    )
    return violations

@router.post("/quick-process")
def quick_process_violations(
    *,
    db: Session = Depends(deps.get_db),
    violation_ids: List[int],
    action: str,  # "approve" or "reject"
    notes: Optional[str] = None,
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Quickly process multiple violations with the same action.
    """
    if action not in ["approve", "reject"]:
        raise HTTPException(
            status_code=400,
            detail="Action must be 'approve' or 'reject'"
        )
    
    processed_violations = []
    failed_violations = []
    
    for violation_id in violation_ids:
        try:
            violation = crud_violation.get_violation(db, violation_id=violation_id)
            if not violation:
                failed_violations.append({
                    "violation_id": violation_id,
                    "error": "Violation not found"
                })
                continue
            
            if violation.status != "pending":
                failed_violations.append({
                    "violation_id": violation_id,
                    "error": "Violation is not pending"
                })
                continue
            
            status = "processed" if action == "approve" else "rejected"
            processing_notes = notes or f"Bulk {action} by officer {current_user.badge_number}"
            
            violation_update = ViolationUpdate(
                status=status,
                processing_notes=processing_notes
            )
            
            updated_violation = crud_violation.update_violation(
                db,
                violation_id=violation_id,
                violation_update=violation_update,
                processed_by=current_user.id
            )
            
            processed_violations.append(updated_violation.id)
            
        except Exception as e:
            failed_violations.append({
                "violation_id": violation_id,
                "error": str(e)
            })
    
    return {
        "message": f"Processed {len(processed_violations)} violations",
        "processed_violations": processed_violations,
        "failed_violations": failed_violations,
        "action": action
    }
