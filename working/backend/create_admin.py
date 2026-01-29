"""
Create Admin Account
Run this script to create a single admin account for initial system setup.

Usage:
    python create_admin.py

This will create an admin user with the following credentials:
    Username: admin
    Password: Admin123!
    Role: Admin (role level 2)
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash


def create_admin():
    """Create a single admin account for system setup"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("Creating Admin Account")
        print("="*60)
        
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("\n⚠️  Admin user already exists!")
            print(f"   Username: {existing_admin.username}")
            print(f"   Email: {existing_admin.email}")
            print(f"   Role: {existing_admin.role} (Admin)")
            print("\nNo changes made.")
            return
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("Admin123!"),
            role=2,  # Admin role
            is_2fa_enabled=False
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("\n✅ Admin account created successfully!")
        print("-" * 60)
        print("Credentials:")
        print(f"   Username: admin")
        print(f"   Password: Admin123!")
        print(f"   Email: admin@example.com")
        print(f"   Role: Admin (level 2)")
        print("-" * 60)
        print("\n⚠️  IMPORTANT: Change the default password after first login!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error creating admin account: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_admin()
