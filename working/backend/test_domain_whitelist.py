"""
Tests for domain whitelist functionality
"""


def test_domain_matching_logic():
    """Test the logic for matching emails against domain wildcards"""
    
    # Simulate whitelisted domains
    whitelisted_domains = ['@example.com', '@test.org', '@company.co.uk']
    
    # Test cases: (email, should_match)
    test_cases = [
        ('user@example.com', True),
        ('john@example.com', True),
        ('admin@subdomain.example.com', True),  # Should match @example.com (subdomain)
        ('user@test.org', True),
        ('someone@company.co.uk', True),
        ('user@different.com', False),
        ('admin@notexample.com', False),  # Should NOT match - different domain
        ('test@example.org', False),  # Different TLD
        ('user@sub.test.org', True),  # Subdomain of test.org
    ]
    
    for email, should_match in test_cases:
        matched = False
        for domain in whitelisted_domains:
            # Extract user domain and whitelisted domain
            user_domain = email.split('@', 1)[1] if '@' in email else ''
            whitelisted_domain = domain[1:]  # Remove '@'
            
            # Check exact match or subdomain match
            if user_domain == whitelisted_domain or user_domain.endswith('.' + whitelisted_domain):
                matched = True
                break
        
        assert matched == should_match, f"Email '{email}' should {'match' if should_match else 'not match'}, but got {matched}"
        print(f"✓ Email '{email}': {'matches' if matched else 'does not match'} (expected: {'match' if should_match else 'no match'})")
    
    print("\n✓ All domain matching tests passed")


def test_exact_email_matching():
    """Test that exact email matches still work"""
    
    # Simulate whitelisted exact emails
    whitelisted_emails = ['specific@email.com', 'admin@company.com']
    
    # Test cases
    test_cases = [
        ('specific@email.com', True),
        ('admin@company.com', True),
        ('different@email.com', False),
        ('specific@other.com', False),
    ]
    
    for email, should_match in test_cases:
        matched = email in whitelisted_emails
        
        assert matched == should_match, f"Email '{email}' should {'match' if should_match else 'not match'}"
        print(f"✓ Email '{email}': {'matches' if matched else 'does not match'} (expected: {'match' if should_match else 'no match'})")
    
    print("\n✓ All exact email matching tests passed")


def test_combined_matching():
    """Test combining exact email and domain matching"""
    
    # Simulate mixed whitelist
    exact_emails = ['admin@special.com']
    domain_emails = ['@example.com', '@test.org']
    
    # Test function similar to what we'll have in the code
    def is_email_allowed(email):
        # Check exact match
        if email in exact_emails:
            return True
        
        # Check domain match
        for domain in domain_emails:
            user_domain = email.split('@', 1)[1] if '@' in email else ''
            whitelisted_domain = domain[1:]  # Remove '@'
            
            if user_domain == whitelisted_domain or user_domain.endswith('.' + whitelisted_domain):
                return True
        
        return False
    
    # Test cases
    test_cases = [
        ('admin@special.com', True),      # Exact match
        ('user@example.com', True),       # Domain match
        ('john@test.org', True),          # Domain match
        ('admin@example.com', True),      # Domain match (not exact)
        ('user@other.com', False),        # No match
        ('dev@sub.example.com', True),    # Subdomain match
    ]
    
    for email, should_match in test_cases:
        matched = is_email_allowed(email)
        assert matched == should_match, f"Email '{email}' should {'be allowed' if should_match else 'be denied'}"
        print(f"✓ Email '{email}': {'allowed' if matched else 'denied'} (expected: {'allowed' if should_match else 'denied'})")
    
    print("\n✓ All combined matching tests passed")


if __name__ == "__main__":
    test_domain_matching_logic()
    test_exact_email_matching()
    test_combined_matching()
    print("\n✓✓✓ All tests passed successfully!")
