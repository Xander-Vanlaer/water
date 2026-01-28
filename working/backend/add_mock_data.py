"""
Add mock allowed emails and test data
Run this with: python add_mock_data.py
"""
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import AllowedEmail, User, Region, Hospital
from app.auth import get_password_hash
from datetime import datetime

def add_mock_data():
    db = SessionLocal()
    
    try:
        print("\n=== Adding Mock Allowed Emails ===")
        
        # Mock emails to whitelist
        mock_emails = [
            "john.doe@hospital.com",
            "jane.smith@medical.org",
            "admin@healthcare.net",
            "doctor.mike@clinic.com",
            "nurse.sarah@hospital.com",
            "tech.alex@healthtech.io",
            "manager.lisa@regional.health",
            "analyst.tom@data.med",
            "supervisor.emma@care.center",
            "operator.david@sensor.systems",
            "@test.com",  # Domain whitelist example
            "@gmail.com"  # Domain whitelist example
        ]
        
        added_count = 0
        for email in mock_emails:
            # Check if already exists
            existing = db.query(AllowedEmail).filter(AllowedEmail.email == email).first()
            if not existing:
                allowed = AllowedEmail(
                    email=email,
                    created_by=None  # System-added
                )
                db.add(allowed)
                print(f"  ✓ Added: {email}")
                added_count += 1
            else:
                print(f"  ⚠️  Already exists: {email}")
        
        db.commit()
        print(f"\n✅ Added {added_count} new emails to whitelist\n")
        
        
        # Optional: Create some test users (you can remove this section if not needed)
        print("=== Creating Mock Users ===")
        mock_users = [
            {
                "username": "john_doe",
                "email": "john.doe@hospital.com",
                "password": "Password123",
                "role": 4  # Hospital User
            },
            {
                "username": "jane_smith",
                "email": "jane.smith@medical.org",
                "password": "SecurePass456",
                "role": 3  # Region Admin
            },
            {
                "username": "doctor_mike",
                "email": "doctor.mike@clinic.com",
                "password": "Medical789",
                "role": 4  # Hospital User
            }
        ]
        
        user_count = 0
        for user_data in mock_users:
            # Check if already exists
            existing = db.query(User).filter(User.username == user_data["username"]).first()
            if not existing:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=get_password_hash(user_data["password"]),
                    role=user_data["role"],
                    created_at=datetime.utcnow()
                )
                db.add(user)
                print(f"  ✓ Created user: {user_data['username']} ({user_data['email']})")
                user_count += 1
            else:
                print(f"  ⚠️  User already exists: {user_data['username']}")
        
        db.commit()
        print(f"\n✅ Created {user_count} new users\n")
        
        
        print("=== Summary ===")
        total_allowed = db.query(AllowedEmail).count()
        total_users = db.query(User).count()
        print(f"Total allowed emails: {total_allowed}")
        print(f"Total users: {total_users}")
        print("\nYou can now register with any of the whitelisted emails!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    add_mock_data()