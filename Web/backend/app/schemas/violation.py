from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ViolationBase(BaseModel):
    license_plate: str
    violation_type: str
    description: Optional[str] = None
    location: str
    violation_time: datetime
    fine_amount: float
    source: str

class ViolationCreate(ViolationBase):
    camera_id: Optional[int] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    evidence_urls: Optional[List[str]] = None

class ViolationUpdate(BaseModel):
    status: Optional[str] = None
    processing_notes: Optional[str] = None

class ViolationReport(BaseModel):
    license_plate: str
    violation_type: str
    description: str
    location: str
    violation_time: datetime
    evidence_files: Optional[List[str]] = None

class ViolationInDB(ViolationBase):
    id: int
    violation_code: str
    status: str
    camera_id: Optional[int] = None
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    processed_by: Optional[int] = None
    processed_at: Optional[datetime] = None
    processing_notes: Optional[str] = None
    reported_by: Optional[int] = None
    evidence_urls: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Violation(ViolationInDB):
    pass

class ViolationLookup(BaseModel):
    license_plate: Optional[str] = None
    violation_code: Optional[str] = None
