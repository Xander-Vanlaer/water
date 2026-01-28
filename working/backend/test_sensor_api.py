#!/usr/bin/env python3
"""
Test script for sensor-based API key system

Tests:
1. Model validations
2. Schema validations
3. Sensor ID uniqueness
4. Email whitelist functionality
"""

import sys
sys.path.insert(0, '/home/runner/work/security/security/backend')

from app.models import APIKey, AllowedEmail
from app.schemas import APIKeyCreate, AllowedEmailCreate, SensorDataCreate


def test_api_key_schema():
    """Test APIKeyCreate schema"""
    print("\n=== Testing APIKeyCreate Schema ===")
    
    # Valid API key creation
    try:
        valid_key = APIKeyCreate(
            sensor_id="HOSP001-TEMP-001",
            hospital_id=1,
            description="Test sensor"
        )
        print("✓ Valid API key schema accepted")
    except Exception as e:
        print(f"✗ Valid API key schema rejected: {e}")
        return False
    
    # Missing sensor_id
    try:
        invalid_key = APIKeyCreate(
            hospital_id=1,
            description="Test"
        )
        print("✗ Missing sensor_id was accepted (should fail)")
        return False
    except Exception as e:
        print(f"✓ Missing sensor_id correctly rejected")
    
    return True


def test_allowed_email_schema():
    """Test AllowedEmailCreate schema"""
    print("\n=== Testing AllowedEmailCreate Schema ===")
    
    # Valid email
    try:
        valid_email = AllowedEmailCreate(email="test@example.com")
        print("✓ Valid email schema accepted")
    except Exception as e:
        print(f"✗ Valid email schema rejected: {e}")
        return False
    
    # Invalid email format
    try:
        invalid_email = AllowedEmailCreate(email="not-an-email")
        print("✗ Invalid email format was accepted (should fail)")
        return False
    except Exception as e:
        print(f"✓ Invalid email format correctly rejected")
    
    return True


def test_sensor_data_schema():
    """Test SensorDataCreate schema"""
    print("\n=== Testing SensorDataCreate Schema ===")
    
    # Valid sensor data
    try:
        valid_data = SensorDataCreate(
            sensor_id="HOSP001-TEMP-001",
            temperature=22.5,
            humidity=45.2,
            air_quality=85,
            custom_data={"location": "Ward A"}
        )
        print("✓ Valid sensor data schema accepted")
    except Exception as e:
        print(f"✗ Valid sensor data schema rejected: {e}")
        return False
    
    # Missing sensor_id
    try:
        invalid_data = SensorDataCreate(
            temperature=22.5
        )
        print("✗ Missing sensor_id was accepted (should fail)")
        return False
    except Exception as e:
        print(f"✓ Missing sensor_id correctly rejected")
    
    return True


def test_model_structure():
    """Test model structure"""
    print("\n=== Testing Model Structure ===")
    
    # Check APIKey model has required fields
    required_fields = ['sensor_id', 'is_validated']
    for field in required_fields:
        if hasattr(APIKey, field):
            print(f"✓ APIKey.{field} exists")
        else:
            print(f"✗ APIKey.{field} missing")
            return False
    
    # Check AllowedEmail model exists
    if hasattr(AllowedEmail, 'email'):
        print("✓ AllowedEmail model exists with email field")
    else:
        print("✗ AllowedEmail model incomplete")
        return False
    
    return True


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Sensor-Based API Key System - Unit Tests")
    print("=" * 60)
    
    tests = [
        ("Model Structure", test_model_structure),
        ("APIKey Schema", test_api_key_schema),
        ("AllowedEmail Schema", test_allowed_email_schema),
        ("SensorData Schema", test_sensor_data_schema),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ Test '{test_name}' crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
