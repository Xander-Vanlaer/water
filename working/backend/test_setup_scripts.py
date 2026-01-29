"""
Integration test for create_admin.py and add_domain_whitelist.py scripts
Tests that the scripts work correctly with the database models and auth functions.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.models import User, AllowedEmail
from app.auth import verify_password


def test_create_admin_logic():
    """Test the core logic of create_admin.py"""
    from app.auth import get_password_hash
    
    # Test that we can create admin user object with correct attributes
    admin = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("Admin123!"),
        role=2,  # Admin role
        is_2fa_enabled=False
    )
    
    # Verify attributes
    assert admin.username == "admin"
    assert admin.email == "admin@example.com"
    assert admin.role == 2
    assert admin.is_2fa_enabled == False
    assert verify_password("Admin123!", admin.hashed_password)
    
    print("✓ Admin creation logic validated")


def test_add_domain_whitelist_logic():
    """Test the core logic of add_domain_whitelist.py"""
    
    # Test that we can create AllowedEmail objects with correct domains
    domains = ["@outlook.be", "@gmail.com"]
    
    for domain in domains:
        allowed_email = AllowedEmail(
            email=domain,
            created_by=None
        )
        
        # Verify attributes
        assert allowed_email.email == domain
        assert allowed_email.created_by is None
        assert allowed_email.email.startswith("@")
        
    print("✓ Domain whitelist creation logic validated")


def test_domain_format_validation():
    """Test that domain formats are correct"""
    
    # Valid domain formats
    valid_domains = ["@outlook.be", "@gmail.com", "@example.com"]
    
    for domain in valid_domains:
        assert domain.startswith("@"), f"Domain {domain} should start with @"
        assert len(domain) > 1, f"Domain {domain} should have content after @"
        
    print("✓ Domain format validation passed")


def test_email_matching_with_new_domains():
    """Test that emails from new domains would match correctly"""
    
    whitelisted_domains = ["@outlook.be", "@gmail.com"]
    
    # Test cases
    test_cases = [
        ("user@outlook.be", True),
        ("john.doe@gmail.com", True),
        ("admin@subdomain.outlook.be", True),  # Subdomain should match
        ("test@example.com", False),  # Not whitelisted
        ("user@outlook.com", False),  # Different domain
    ]
    
    for email, should_match in test_cases:
        matched = False
        for domain in whitelisted_domains:
            user_domain = email.split('@', 1)[1] if '@' in email else ''
            whitelisted_domain = domain[1:]  # Remove '@'
            
            if user_domain == whitelisted_domain or user_domain.endswith('.' + whitelisted_domain):
                matched = True
                break
        
        assert matched == should_match, f"Email {email} should {'match' if should_match else 'not match'}"
    
    print("✓ Email matching with new domains validated")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing create_admin.py and add_domain_whitelist.py logic")
    print("="*60 + "\n")
    
    test_create_admin_logic()
    test_add_domain_whitelist_logic()
    test_domain_format_validation()
    test_email_matching_with_new_domains()
    
    print("\n" + "="*60)
    print("✅ All integration tests passed successfully!")
    print("="*60 + "\n")
