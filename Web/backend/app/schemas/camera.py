from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CameraBase(BaseModel):
    camera_code: str
    name: str
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    camera_type: str
    ip_address: Optional[str] = None
    rtsp_url: Optional[str] = None
    description: Optional[str] = None

class CameraCreate(CameraBase):
    pass

class CameraUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    camera_type: Optional[str] = None
    status: Optional[str] = None
    ip_address: Optional[str] = None
    rtsp_url: Optional[str] = None
    description: Optional[str] = None
    last_maintenance: Optional[datetime] = None

class CameraInDB(CameraBase):
    id: int
    status: str
    installation_date: Optional[datetime] = None
    last_maintenance: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class Camera(CameraInDB):
    pass
