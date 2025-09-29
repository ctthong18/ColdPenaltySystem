"""
Script to create database tables using Alembic migrations
"""
from alembic.config import Config
from alembic import command
import os

def create_database():
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the backend directory
    backend_dir = os.path.dirname(script_dir)
    
    # Path to alembic.ini
    alembic_cfg_path = os.path.join(backend_dir, "alembic.ini")
    
    # Create Alembic configuration
    alembic_cfg = Config(alembic_cfg_path)
    
    # Generate initial migration
    try:
        command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
        print("✅ Generated initial migration")
    except Exception as e:
        print(f"⚠️  Migration generation failed (might already exist): {e}")
    
    # Run migrations
    try:
        command.upgrade(alembic_cfg, "head")
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    create_database()
