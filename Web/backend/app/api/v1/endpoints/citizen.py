from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
import uuid

from app.api import deps
from app.crud import violation as crud_violation, user as crud_user
from app.schemas.violation import Violation, ViolationReport
from app.schemas.user import UserUpdate
from app.models.user import User
from app.core.config import settings

router = APIRouter()

@router.get("/my-violations", response_model=List[Violation])
def get_my_violations(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get violations reported by current citizen.
    """
    query = db.query(crud_violation.Violation).filter(
        crud_violation.Violation.reported_by == current_user.id
    )
    
    if status:
        query = query.filter(crud_violation.Violation.status == status)
    
    violations = query.offset(skip).limit(limit).all()
    return violations

@router.post("/report-violation", response_model=Violation)
async def report_violation(
    *,
    db: Session = Depends(deps.get_db),
    violation_report: ViolationReport,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Report a traffic violation as a citizen.
    """
    from app.schemas.violation import ViolationCreate
    
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

@router.post("/upload-evidence")
async def upload_evidence_for_report(
    *,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Upload evidence files for violation reports.
    """
    uploaded_files = []
    
    for file in files:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "video/mp4"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file.content_type} not allowed"
            )
        
        # Generate unique filename
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"citizen_{current_user.id}_{uuid.uuid4()}.{file_extension}"
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

@router.get("/my-reports-statistics")
def get_my_reports_statistics(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get statistics of citizen's violation reports.
    """
    from app.models.violation import Violation
    
    total_reports = db.query(Violation).filter(
        Violation.reported_by == current_user.id
    ).count()
    
    pending_reports = db.query(Violation).filter(
        Violation.reported_by == current_user.id,
        Violation.status == "pending"
    ).count()
    
    processed_reports = db.query(Violation).filter(
        Violation.reported_by == current_user.id,
        Violation.status == "processed"
    ).count()
    
    rejected_reports = db.query(Violation).filter(
        Violation.reported_by == current_user.id,
        Violation.status == "rejected"
    ).count()
    
    return {
        "total_reports": total_reports,
        "pending_reports": pending_reports,
        "processed_reports": processed_reports,
        "rejected_reports": rejected_reports,
        "citizen_name": current_user.full_name,
        "citizen_id": current_user.citizen_id
    }

@router.put("/update-profile")
def update_my_profile(
    *,
    db: Session = Depends(deps.get_db),
    user_update: UserUpdate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Update citizen's profile information.
    """
    # Citizens can only update certain fields
    allowed_fields = ["full_name", "phone", "address"]
    update_data = {}
    
    for field, value in user_update.dict(exclude_unset=True).items():
        if field in allowed_fields:
            update_data[field] = value
    
    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No valid fields to update"
        )
    
    # Create a new UserUpdate with only allowed fields
    filtered_update = UserUpdate(**update_data)
    
    updated_user = crud_user.update_user(
        db, 
        user_id=current_user.id, 
        user_update=filtered_update
    )
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "message": "Profile updated successfully",
        "user": updated_user
    }

@router.get("/violation-types")
def get_violation_types(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get list of available violation types for reporting.
    """
    violation_types = [
        {
            "code": "speeding",
            "name": "Vượt quá tốc độ cho phép",
            "description": "Phương tiện vượt quá tốc độ quy định"
        },
        {
            "code": "red_light",
            "name": "Vượt đèn đỏ",
            "description": "Không tuân thủ tín hiệu đèn giao thông"
        },
        {
            "code": "wrong_parking",
            "name": "Đỗ xe sai quy định",
            "description": "Đỗ xe không đúng nơi quy định"
        },
        {
            "code": "no_helmet",
            "name": "Không đội mũ bảo hiểm",
            "description": "Người điều khiển xe máy không đội mũ bảo hiểm"
        },
        {
            "code": "wrong_lane",
            "name": "Đi sai làn đường",
            "description": "Không đi đúng làn đường quy định"
        },
        {
            "code": "phone_driving",
            "name": "Sử dụng điện thoại khi lái xe",
            "description": "Sử dụng thiết bị di động khi điều khiển phương tiện"
        },
        {
            "code": "no_license",
            "name": "Không có giấy phép lái xe",
            "description": "Điều khiển phương tiện không có bằng lái hợp lệ"
        },
        {
            "code": "other",
            "name": "Vi phạm khác",
            "description": "Các vi phạm khác không thuộc danh mục trên"
        }
    ]
    
    return {
        "violation_types": violation_types
    }

@router.get("/report-guidelines")
def get_report_guidelines(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get guidelines for reporting violations.
    """
    guidelines = {
        "general_guidelines": [
            "Chỉ báo cáo những vi phạm mà bạn trực tiếp chứng kiến",
            "Cung cấp thông tin chính xác và đầy đủ",
            "Đính kèm bằng chứng rõ ràng (ảnh, video)",
            "Ghi rõ thời gian, địa điểm vi phạm"
        ],
        "evidence_requirements": [
            "Ảnh/video phải rõ nét, không bị mờ",
            "Phải thể hiện rõ biển số xe vi phạm",
            "Phải thể hiện rõ hành vi vi phạm",
            "Kích thước file tối đa 10MB"
        ],
        "supported_formats": [
            "Ảnh: JPEG, PNG, JPG",
            "Video: MP4"
        ],
        "processing_time": "Báo cáo sẽ được xử lý trong vòng 3-5 ngày làm việc",
        "contact_info": {
            "hotline": "1900-xxxx",
            "email": "support@phatnguoi.gov.vn"
        }
    }
    
    return guidelines

@router.get("/my-report/{report_id}", response_model=Violation)
def get_my_report_detail(
    *,
    db: Session = Depends(deps.get_db),
    report_id: int,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get detailed information about a specific report.
    """
    from app.models.violation import Violation
    
    violation = db.query(Violation).filter(
        Violation.id == report_id,
        Violation.reported_by == current_user.id
    ).first()
    
    if not violation:
        raise HTTPException(
            status_code=404, 
            detail="Report not found or you don't have permission to view it"
        )
    
    return violation
