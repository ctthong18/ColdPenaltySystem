from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func, and_

from app.api import deps
from app.models.violation import Violation
from app.models.camera import Camera
from app.models.user import User

router = APIRouter()

@router.get("/violation-trends")
def get_violation_trends(
    db: Session = Depends(deps.get_db),
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Get violation trends over time for reports and analytics.
    """
    date_from = datetime.utcnow() - timedelta(days=days)
    
    # Group violations by date (simplified version)
    # In a real implementation, you'd use proper SQL grouping
    violations_by_day = []
    for i in range(days):
        day = date_from + timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        count = db.query(Violation).filter(
            and_(
                Violation.violation_time >= day_start,
                Violation.violation_time < day_end
            )
        ).count()
        
        violations_by_day.append({
            "date": day_start.strftime("%Y-%m-%d"),
            "count": count
        })
    
    return {
        "period_days": days,
        "data": violations_by_day
    }

@router.get("/performance-report")
def get_performance_report(
    db: Session = Depends(deps.get_db),
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Get performance report for officers (authority only) or self-report for officers.
    """
    date_from = datetime.utcnow() - timedelta(days=days)
    
    if current_user.role == "authority":
        # Authority can see all officers' performance
        officers = db.query(User).filter(User.role == "officer", User.is_active == True).all()
        
        performance_data = []
        for officer in officers:
            processed_count = db.query(Violation).filter(
                and_(
                    Violation.processed_by == officer.id,
                    Violation.processed_at >= date_from
                )
            ).count()
            
            performance_data.append({
                "officer_id": officer.id,
                "officer_name": officer.full_name,
                "badge_number": officer.badge_number,
                "processed_violations": processed_count,
                "department": officer.department
            })
        
        return {
            "period_days": days,
            "officers_performance": performance_data
        }
    
    else:
        # Officer can only see their own performance
        processed_count = db.query(Violation).filter(
            and_(
                Violation.processed_by == current_user.id,
                Violation.processed_at >= date_from
            )
        ).count()
        
        return {
            "period_days": days,
            "officer_performance": {
                "officer_name": current_user.full_name,
                "badge_number": current_user.badge_number,
                "processed_violations": processed_count,
                "department": current_user.department
            }
        }

@router.get("/camera-efficiency")
def get_camera_efficiency(
    db: Session = Depends(deps.get_db),
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Get camera efficiency report showing violations detected per camera.
    """
    date_from = datetime.utcnow() - timedelta(days=days)
    
    cameras = db.query(Camera).filter(Camera.status == "active").all()
    
    camera_efficiency = []
    for camera in cameras:
        violation_count = db.query(Violation).filter(
            and_(
                Violation.camera_id == camera.id,
                Violation.violation_time >= date_from
            )
        ).count()
        
        camera_efficiency.append({
            "camera_id": camera.id,
            "camera_code": camera.camera_code,
            "camera_name": camera.name,
            "location": camera.location,
            "camera_type": camera.camera_type,
            "violations_detected": violation_count,
            "efficiency_rate": violation_count / days  # violations per day
        })
    
    # Sort by violations detected (descending)
    camera_efficiency.sort(key=lambda x: x["violations_detected"], reverse=True)
    
    return {
        "period_days": days,
        "camera_efficiency": camera_efficiency,
        "total_cameras": len(cameras)
    }

@router.get("/export-data")
def export_violation_data(
    db: Session = Depends(deps.get_db),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    status: Optional[str] = Query(None),
    violation_type: Optional[str] = Query(None),
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Export violation data for reports (simplified version).
    In a real implementation, this would generate CSV/Excel files.
    """
    if not date_from:
        date_from = datetime.utcnow() - timedelta(days=30)
    if not date_to:
        date_to = datetime.utcnow()
    
    query = db.query(Violation).filter(
        and_(
            Violation.violation_time >= date_from,
            Violation.violation_time <= date_to
        )
    )
    
    if status:
        query = query.filter(Violation.status == status)
    if violation_type:
        query = query.filter(Violation.violation_type.ilike(f"%{violation_type}%"))
    
    violations = query.all()
    
    export_data = []
    for violation in violations:
        export_data.append({
            "violation_code": violation.violation_code,
            "license_plate": violation.license_plate,
            "violation_type": violation.violation_type,
            "location": violation.location,
            "violation_time": violation.violation_time.isoformat(),
            "fine_amount": violation.fine_amount,
            "status": violation.status,
            "source": violation.source,
            "processed_at": violation.processed_at.isoformat() if violation.processed_at else None
        })
    
    return {
        "export_summary": {
            "total_records": len(export_data),
            "date_from": date_from.isoformat(),
            "date_to": date_to.isoformat(),
            "filters": {
                "status": status,
                "violation_type": violation_type
            }
        },
        "data": export_data
    }
