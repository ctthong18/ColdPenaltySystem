from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraUpdate

def get_camera(db: Session, camera_id: int) -> Optional[Camera]:
    return db.query(Camera).filter(Camera.id == camera_id).first()

def get_camera_by_code(db: Session, camera_code: str) -> Optional[Camera]:
    return db.query(Camera).filter(Camera.camera_code == camera_code).first()

def get_cameras(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None,
    camera_type: Optional[str] = None
) -> List[Camera]:
    query = db.query(Camera)
    
    if status:
        query = query.filter(Camera.status == status)
    if camera_type:
        query = query.filter(Camera.camera_type == camera_type)
    
    return query.offset(skip).limit(limit).all()

def create_camera(db: Session, camera: CameraCreate) -> Camera:
    db_camera = Camera(**camera.dict())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera

def update_camera(db: Session, camera_id: int, camera_update: CameraUpdate) -> Optional[Camera]:
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if db_camera:
        update_data = camera_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_camera, field, value)
        db.commit()
        db.refresh(db_camera)
    return db_camera

def delete_camera(db: Session, camera_id: int) -> bool:
    db_camera = db.query(Camera).filter(Camera.id == camera_id).first()
    if db_camera:
        db.delete(db_camera)
        db.commit()
        return True
    return False

def get_camera_statistics(db: Session):
    """Get camera statistics"""
    total_cameras = db.query(Camera).count()
    active_cameras = db.query(Camera).filter(Camera.status == "active").count()
    inactive_cameras = db.query(Camera).filter(Camera.status == "inactive").count()
    maintenance_cameras = db.query(Camera).filter(Camera.status == "maintenance").count()
    
    return {
        "total_cameras": total_cameras,
        "active_cameras": active_cameras,
        "inactive_cameras": inactive_cameras,
        "maintenance_cameras": maintenance_cameras
    }
