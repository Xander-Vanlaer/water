"""
Add Domain Whitelist
Run this script to add email domains to the whitelist.

Usage:
    python add_domain_whitelist.py

This will add the following domains to the whitelist:
    - @outlook.be
    - @gmail.com

Users with emails from these domains will be able to register.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import AllowedEmail


def add_domain_whitelist():
    """Add required email domains to the whitelist"""
    db = SessionLocal()
    
    try:
        print("\n" + "="*60)
        print("Adding Email Domains to Whitelist")
        print("="*60)
        
        # Domains to whitelist
        domains = [
            "@outlook.be",
            "@gmail.com"
        ]
        
        added_count = 0
        existing_count = 0
        
        for domain in domains:
            # Check if domain already exists
            existing = db.query(AllowedEmail).filter(AllowedEmail.email == domain).first()
            
            if not existing:
                # Add new domain
                allowed_email = AllowedEmail(
                    email=domain,
                    created_by=None  # System-added
                )
                db.add(allowed_email)
                print(f"✓ Added domain: {domain}")
                added_count += 1
            else:
                print(f"⚠️  Domain already exists: {domain}")
                existing_count += 1
        
        db.commit()
        
        print("-" * 60)
        print(f"\n✅ Whitelist updated successfully!")
        print(f"   Added: {added_count} domain(s)")
        print(f"   Already existed: {existing_count} domain(s)")
        
        # Show total whitelisted entries
        total = db.query(AllowedEmail).count()
        print(f"   Total whitelisted entries: {total}")
        print("\n" + "="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error adding domains to whitelist: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_domain_whitelist()
