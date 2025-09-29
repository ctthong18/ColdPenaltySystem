from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True, index=True)
    camera_code = Column(String(20), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)
    location = Column(String(200), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    camera_type = Column(String(50), nullable=False)  # speed, red_light, general
    status = Column(String(20), default="active")  # active, inactive, maintenance
    ip_address = Column(String(45))
    rtsp_url = Column(String(500))
    description = Column(Text)
    installation_date = Column(DateTime(timezone=True))
    last_maintenance = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    violations = relationship("Violation", back_populates="camera")
