from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
from app.models.violation import Violation
from app.schemas.violation import ViolationCreate, ViolationUpdate
import uuid

def generate_violation_code() -> str:
    """Generate unique violation code"""
    return f"VL{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"

def get_violation(db: Session, violation_id: int) -> Optional[Violation]:
    return db.query(Violation).filter(Violation.id == violation_id).first()

def get_violation_by_code(db: Session, violation_code: str) -> Optional[Violation]:
    return db.query(Violation).filter(Violation.violation_code == violation_code).first()

def get_violations(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    license_plate: Optional[str] = None,
    violation_type: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
) -> List[Violation]:
    query = db.query(Violation)
    
    if status:
        query = query.filter(Violation.status == status)
    if license_plate:
        query = query.filter(Violation.license_plate.ilike(f"%{license_plate}%"))
    if violation_type:
        query = query.filter(Violation.violation_type.ilike(f"%{violation_type}%"))
    if date_from:
        query = query.filter(Violation.violation_time >= date_from)
    if date_to:
        query = query.filter(Violation.violation_time <= date_to)
    
    return query.order_by(desc(Violation.created_at)).offset(skip).limit(limit).all()

def get_violations_by_license_plate(db: Session, license_plate: str) -> List[Violation]:
    return db.query(Violation).filter(
        Violation.license_plate.ilike(f"%{license_plate}%")
    ).order_by(desc(Violation.violation_time)).all()

def create_violation(db: Session, violation: ViolationCreate, reported_by: Optional[int] = None) -> Violation:
    violation_code = generate_violation_code()
    db_violation = Violation(
        violation_code=violation_code,
        license_plate=violation.license_plate,
        violation_type=violation.violation_type,
        description=violation.description,
        location=violation.location,
        violation_time=violation.violation_time,
        fine_amount=violation.fine_amount,
        source=violation.source,
        camera_id=violation.camera_id,
        image_url=violation.image_url,
        video_url=violation.video_url,
        reported_by=reported_by,
        evidence_urls=",".join(violation.evidence_urls) if violation.evidence_urls else None,
    )
    db.add(db_violation)
    db.commit()
    db.refresh(db_violation)
    return db_violation

def update_violation(
    db: Session, 
    violation_id: int, 
    violation_update: ViolationUpdate,
    processed_by: int
) -> Optional[Violation]:
    db_violation = db.query(Violation).filter(Violation.id == violation_id).first()
    if db_violation:
        update_data = violation_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_violation, field, value)
        
        db_violation.processed_by = processed_by
        db_violation.processed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_violation)
    return db_violation

def get_violation_statistics(db: Session, days: int = 30):
    """Get violation statistics for the last N days"""
    date_from = datetime.utcnow() - timedelta(days=days)
    
    total_violations = db.query(Violation).filter(
        Violation.created_at >= date_from
    ).count()
    
    pending_violations = db.query(Violation).filter(
        and_(Violation.status == "pending", Violation.created_at >= date_from)
    ).count()
    
    processed_violations = db.query(Violation).filter(
        and_(Violation.status == "processed", Violation.created_at >= date_from)
    ).count()
    
    paid_violations = db.query(Violation).filter(
        and_(Violation.status == "paid", Violation.created_at >= date_from)
    ).count()
    
    return {
        "total_violations": total_violations,
        "pending_violations": pending_violations,
        "processed_violations": processed_violations,
        "paid_violations": paid_violations,
        "period_days": days
    }
