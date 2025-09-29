from typing import Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.api import deps
from app.crud import violation as crud_violation, camera as crud_camera, user as crud_user
from app.models.user import User

router = APIRouter()

@router.get("/dashboard")
def get_dashboard_statistics(
    db: Session = Depends(deps.get_db),
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Get comprehensive dashboard statistics. For officers and authority users.
    """
    violation_stats = crud_violation.get_violation_statistics(db, days=days)
    camera_stats = crud_camera.get_camera_statistics(db)
    
    # User statistics (only for authority)
    user_stats = {}
    if current_user.role == "authority":
        total_users = len(crud_user.get_users(db))
        officers = len(crud_user.get_users_by_role(db, "officer"))
        citizens = len(crud_user.get_users_by_role(db, "citizen"))
        authorities = len(crud_user.get_users_by_role(db, "authority"))
        
        user_stats = {
            "total_users": total_users,
            "officers": officers,
            "citizens": citizens,
            "authorities": authorities
        }
    
    return {
        "violations": violation_stats,
        "cameras": camera_stats,
        "users": user_stats,
        "period_days": days
    }

@router.get("/violations/by-type")
def get_violations_by_type(
    db: Session = Depends(deps.get_db),
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Get violation statistics grouped by type. For officers and authority users.
    """
    date_from = datetime.utcnow() - timedelta(days=days)
    
    # This would need a more complex query in a real implementation
    # For now, returning sample data structure
    return {
        "speeding": 45,
        "red_light": 32,
        "parking": 28,
        "no_helmet": 15,
        "wrong_lane": 12,
        "period_days": days
    }

@router.get("/violations/by-location")
def get_violations_by_location(
    db: Session = Depends(deps.get_db),
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Get violation statistics grouped by location. For officers and authority users.
    """
    date_from = datetime.utcnow() - timedelta(days=days)
    
    # This would need a more complex query in a real implementation
    # For now, returning sample data structure
    return {
        "Đường Nguyễn Huệ": 25,
        "Đường Lê Lợi": 20,
        "Đường Trần Hưng Đạo": 18,
        "Đường Hai Bà Trưng": 15,
        "Đường Điện Biên Phủ": 12,
        "period_days": days
    }
