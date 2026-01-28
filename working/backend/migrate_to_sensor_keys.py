#!/usr/bin/env python3
"""
Post-migration script for sensor-based API key system

This script helps migrate existing data after running the database migration:
1. Adds existing user emails to the allowed_emails whitelist
2. Optionally updates existing API keys with sensor IDs

Run this after applying migration 002_sensor_api_keys:
    docker compose exec backend python migrate_to_sensor_keys.py
"""

import sys
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import User, APIKey, AllowedEmail, Hospital


def add_existing_emails_to_whitelist(db: Session):
    """Add all existing user emails to the whitelist"""
    print("\n=== Adding existing user emails to whitelist ===")
    
    # Get all existing users
    users = db.query(User).all()
    
    if not users:
        print("No existing users found.")
        return
    
    added_count = 0
    skipped_count = 0
    
    for user in users:
        # Check if email already in whitelist
        existing = db.query(AllowedEmail).filter(AllowedEmail.email == user.email).first()
        
        if existing:
            print(f"  ⚠️  Email {user.email} already whitelisted (skipped)")
            skipped_count += 1
        else:
            allowed_email = AllowedEmail(
                email=user.email,
                created_by=None  # System migration
            )
            db.add(allowed_email)
            print(f"  ✓ Added {user.email} to whitelist")
            added_count += 1
    
    db.commit()
    print(f"\n✅ Added {added_count} emails to whitelist ({skipped_count} already existed)")


def update_api_keys_with_sensor_ids(db: Session):
    """Update existing API keys with auto-generated sensor IDs"""
    print("\n=== Updating existing API keys with sensor IDs ===")
    
    # Get all API keys without sensor_id
    api_keys = db.query(APIKey).filter(APIKey.sensor_id == None).all()
    
    if not api_keys:
        print("No API keys without sensor_id found.")
        return
    
    updated_count = 0
    
    for api_key in api_keys:
        # Get hospital info
        hospital = db.query(Hospital).filter(Hospital.id == api_key.hospital_id).first()
        
        if not hospital:
            print(f"  ⚠️  Warning: Hospital not found for API key {api_key.id}")
            continue
        
        # Generate sensor_id based on hospital code and API key ID
        sensor_id = f"{hospital.code}-LEGACY-{api_key.id:03d}"
        
        # Check if this sensor_id already exists
        existing = db.query(APIKey).filter(APIKey.sensor_id == sensor_id).first()
        if existing:
            # Try with different suffix
            sensor_id = f"{hospital.code}-LEGACY-{api_key.id:04d}"
        
        api_key.sensor_id = sensor_id
        api_key.is_validated = True  # Auto-validate legacy keys
        
        print(f"  ✓ Updated API key {api_key.id}: sensor_id = {sensor_id}")
        updated_count += 1
    
    db.commit()
    print(f"\n✅ Updated {updated_count} API keys with sensor IDs")


def main():
    print("=" * 60)
    print("Post-Migration Script: Sensor-Based API Keys")
    print("=" * 60)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Step 1: Add existing emails to whitelist
        add_existing_emails_to_whitelist(db)
        
        # Step 2: Ask if user wants to update API keys
        print("\n" + "=" * 60)
        response = input("\nDo you want to update existing API keys with sensor IDs? (y/n): ")
        
        if response.lower() in ['y', 'yes']:
            update_api_keys_with_sensor_ids(db)
        else:
            print("\nSkipped API key updates. You can:")
            print("  - Run this script again later")
            print("  - Manually update API keys in the database")
            print("  - Regenerate API keys through the admin interface")
        
        print("\n" + "=" * 60)
        print("✅ Migration complete!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Review the allowed_emails table")
        print("  2. Add any additional emails that should be whitelisted")
        print("  3. Notify users about the new registration requirements")
        print("  4. If API keys were updated, notify sensor operators")
        print("  5. Consider regenerating API keys for better security")
        
    except Exception as e:
        print(f"\n❌ Error during migration: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
