"""
Script to seed initial data for the traffic violation system
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.crud.user import create_user
from app.crud.camera import create_camera
from app.schemas.user import UserCreate
from app.schemas.camera import CameraCreate
from datetime import datetime

def seed_data():
    db: Session = SessionLocal()
    
    try:
        # Create authority user
        authority_user = UserCreate(
            username="admin",
            email="admin@phatnguoi.gov.vn",
            password="admin123",
            full_name="Quản trị viên hệ thống",
            phone="0123456789",
            role="authority"
        )
        
        try:
            create_user(db, authority_user)
            print("✅ Created authority user: admin/admin123")
        except Exception as e:
            print(f"⚠️  Authority user might already exist: {e}")
        
        # Create officer users
        officers = [
            {
                "username": "officer1",
                "email": "officer1@phatnguoi.gov.vn",
                "password": "officer123",
                "full_name": "Nguyễn Văn An",
                "phone": "0987654321",
                "badge_number": "CS001",
                "department": "Phòng CSGT Quận 1"
            },
            {
                "username": "officer2",
                "email": "officer2@phatnguoi.gov.vn",
                "password": "officer123",
                "full_name": "Trần Thị Bình",
                "phone": "0987654322",
                "badge_number": "CS002",
                "department": "Phòng CSGT Quận 3"
            }
        ]
        
        for officer_data in officers:
            officer_user = UserCreate(
                username=officer_data["username"],
                email=officer_data["email"],
                password=officer_data["password"],
                full_name=officer_data["full_name"],
                phone=officer_data["phone"],
                role="officer",
                badge_number=officer_data["badge_number"],
                department=officer_data["department"]
            )
            
            try:
                create_user(db, officer_user)
                print(f"✅ Created officer: {officer_data['username']}/officer123")
            except Exception as e:
                print(f"⚠️  Officer {officer_data['username']} might already exist: {e}")
        
        # Create citizen user
        citizen_user = UserCreate(
            username="citizen1",
            email="citizen1@gmail.com",
            password="citizen123",
            full_name="Lê Văn Công",
            phone="0912345678",
            role="citizen",
            citizen_id="123456789012",
            address="123 Đường ABC, Quận 1, TP.HCM"
        )
        
        try:
            create_user(db, citizen_user)
            print("✅ Created citizen user: citizen1/citizen123")
        except Exception as e:
            print(f"⚠️  Citizen user might already exist: {e}")
        
        # Create sample cameras
        cameras = [
            {
                "camera_code": "CAM001",
                "name": "Camera Nguyễn Huệ - Đồng Khởi",
                "location": "Giao lộ Nguyễn Huệ - Đồng Khởi, Quận 1",
                "latitude": 10.7769,
                "longitude": 106.7009,
                "camera_type": "speed",
                "ip_address": "192.168.1.101"
            },
            {
                "camera_code": "CAM002",
                "name": "Camera Lê Lợi - Pasteur",
                "location": "Giao lộ Lê Lợi - Pasteur, Quận 1",
                "latitude": 10.7796,
                "longitude": 106.6947,
                "camera_type": "red_light",
                "ip_address": "192.168.1.102"
            },
            {
                "camera_code": "CAM003",
                "name": "Camera Trần Hưng Đạo - Nguyễn Thái Học",
                "location": "Giao lộ Trần Hưng Đạo - Nguyễn Thái Học, Quận 1",
                "latitude": 10.7691,
                "longitude": 106.6958,
                "camera_type": "general",
                "ip_address": "192.168.1.103"
            }
        ]
        
        for camera_data in cameras:
            camera = CameraCreate(**camera_data)
            
            try:
                create_camera(db, camera)
                print(f"✅ Created camera: {camera_data['camera_code']}")
            except Exception as e:
                print(f"⚠️  Camera {camera_data['camera_code']} might already exist: {e}")
        
        print("\n🎉 Database seeding completed!")
        print("\nDefault accounts:")
        print("Authority: admin / admin123")
        print("Officer 1: officer1 / officer123")
        print("Officer 2: officer2 / officer123")
        print("Citizen: citizen1 / citizen123")
        
    except Exception as e:
        print(f"❌ Seeding failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
