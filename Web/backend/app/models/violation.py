from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)
    violation_code = Column(String(20), unique=True, index=True, nullable=False)
    license_plate = Column(String(20), nullable=False, index=True)
    violation_type = Column(String(100), nullable=False)
    description = Column(Text)
    location = Column(String(200), nullable=False)
    violation_time = Column(DateTime(timezone=True), nullable=False)
    fine_amount = Column(Float, nullable=False)
    status = Column(String(20), default="pending")  # pending, processed, paid, appealed
    source = Column(String(20), nullable=False)  # camera, report
    
    # Camera related fields
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    image_url = Column(String(500))
    video_url = Column(String(500))
    
    # Processing fields
    processed_by = Column(Integer, ForeignKey("users.id"))
    processed_at = Column(DateTime(timezone=True))
    processing_notes = Column(Text)
    
    # Report related fields (if source is report)
    reported_by = Column(Integer, ForeignKey("users.id"))
    evidence_urls = Column(Text)  # JSON array of evidence file URLs
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    camera = relationship("Camera", back_populates="violations")
    processor = relationship("User", foreign_keys=[processed_by])
    reporter = relationship("User", foreign_keys=[reported_by])
