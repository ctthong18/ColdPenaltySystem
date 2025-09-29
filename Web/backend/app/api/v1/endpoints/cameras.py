from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import camera as crud_camera
from app.schemas.camera import Camera, CameraCreate, CameraUpdate
from app.models.user import User

router = APIRouter()

@router.get("/", response_model=List[Camera])
def read_cameras(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None),
    camera_type: Optional[str] = Query(None),
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Retrieve cameras with filters. For officers and authority users.
    """
    cameras = crud_camera.get_cameras(
        db, 
        skip=skip, 
        limit=limit,
        status=status,
        camera_type=camera_type
    )
    return cameras

@router.get("/statistics")
def get_camera_statistics(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Get camera statistics. For officers and authority users.
    """
    return crud_camera.get_camera_statistics(db)

@router.get("/{camera_id}", response_model=Camera)
def read_camera(
    *,
    db: Session = Depends(deps.get_db),
    camera_id: int,
    current_user: User = Depends(deps.get_current_officer_user),
) -> Any:
    """
    Get camera by ID. For officers and authority users.
    """
    camera = crud_camera.get_camera(db, camera_id=camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    return camera

@router.post("/", response_model=Camera)
def create_camera(
    *,
    db: Session = Depends(deps.get_db),
    camera_in: CameraCreate,
    current_user: User = Depends(deps.get_current_authority_user),
) -> Any:
    """
    Create new camera. Only for authority users.
    """
    camera = crud_camera.get_camera_by_code(db, camera_code=camera_in.camera_code)
    if camera:
        raise HTTPException(
            status_code=400,
            detail="Camera with this code already exists in the system.",
        )
    camera = crud_camera.create_camera(db, camera=camera_in)
    return camera

@router.put("/{camera_id}", response_model=Camera)
def update_camera(
    *,
    db: Session = Depends(deps.get_db),
    camera_id: int,
    camera_in: CameraUpdate,
    current_user: User = Depends(deps.get_current_authority_user),
) -> Any:
    """
    Update a camera. Only for authority users.
    """
    camera = crud_camera.get_camera(db, camera_id=camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    camera = crud_camera.update_camera(db, camera_id=camera_id, camera_update=camera_in)
    return camera

@router.delete("/{camera_id}")
def delete_camera(
    *,
    db: Session = Depends(deps.get_db),
    camera_id: int,
    current_user: User = Depends(deps.get_current_authority_user),
) -> Any:
    """
    Delete a camera. Only for authority users.
    """
    camera = crud_camera.get_camera(db, camera_id=camera_id)
    if not camera:
        raise HTTPException(status_code=404, detail="Camera not found")
    success = crud_camera.delete_camera(db, camera_id=camera_id)
    if success:
        return {"message": "Camera deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete camera")
