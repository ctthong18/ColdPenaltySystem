from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime

from app.api import deps
from app.crud import violation as crud_violation
from app.schemas.violation import Violation, ViolationCreate, ViolationUpdate, ViolationReport, ViolationLookup
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[Violation])
def read_violations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None),
    license_plate: Optional[str] = Query(None),
    violation_type: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Retrieve violations with filters. For officers and authority users.
    """
    violations = crud_violation.get_violations(
        db, 
        skip=skip, 
        limit=limit,
        status=status,
        license_plate=license_plate,
        violation_type=violation_type,
        date_from=date_from,
        date_to=date_to
    )
    return violations

@router.get("/lookup", response_model=List[Violation])
def lookup_violations(
    db: Session = Depends(deps.get_db),
    license_plate: Optional[str] = Query(None),
    violation_code: Optional[str] = Query(None),
) -> Any:
    """
    Public endpoint to lookup violations by license plate or violation code.
    """
    if not license_plate and not violation_code:
        raise HTTPException(
            status_code=400,
            detail="Either license_plate or violation_code must be provided"
        )
    
    if violation_code:
        violation = crud_violation.get_violation_by_code(db, violation_code)
        return [violation] if violation else []
    
    if license_plate:
        violations = crud_violation.get_violations_by_license_plate(db, license_plate)
        return violations
    
    return []

@router.get("/statistics")
def get_violation_statistics(
    db: Session = Depends(deps.get_db),
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Get violation statistics. For officers and authority users.
    """
    return crud_violation.get_violation_statistics(db, days=days)

@router.get("/{violation_id}", response_model=Violation)
def read_violation(
    *,
    db: Session = Depends(deps.get_db),
    violation_id: int,
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Get violation by ID. For officers and authority users.
    """
    violation = crud_violation.get_violation(db, violation_id=violation_id)
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")
    return violation

@router.post("/", response_model=Violation)
def create_violation(
    *,
    db: Session = Depends(deps.get_db),
    violation_in: ViolationCreate,
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Create new violation. For officers and authority users.
    """
    violation = crud_violation.create_violation(db, violation=violation_in)
    return violation

@router.post("/report", response_model=Violation)
def report_violation(
    *,
    db: Session = Depends(deps.get_db),
    violation_report: ViolationReport,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Report a violation by citizen.
    """
    violation_data = ViolationCreate(
        license_plate=violation_report.license_plate,
        violation_type=violation_report.violation_type,
        description=violation_report.description,
        location=violation_report.location,
        violation_time=violation_report.violation_time,
        fine_amount=0.0,  # Will be set by authority
        source="report",
        evidence_urls=violation_report.evidence_files
    )
    violation = crud_violation.create_violation(
        db, 
        violation=violation_data, 
        reported_by=current_user.id
    )
    return violation

@router.put("/{violation_id}", response_model=Violation)
def update_violation(
    *,
    db: Session = Depends(deps.get_db),
    violation_id: int,
    violation_in: ViolationUpdate,
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Update a violation. For officers and authority users.
    """
    violation = crud_violation.get_violation(db, violation_id=violation_id)
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")
    violation = crud_violation.update_violation(
        db, 
        violation_id=violation_id, 
        violation_update=violation_in,
        processed_by=current_user.id
    )
    return violation
