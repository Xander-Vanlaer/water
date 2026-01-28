# Quick Start Guide: Sensor-Based API Key System

## What Changed?

### Before (Hospital-Based)
```
API Key → Hospital ID → Multiple Sensors
❌ One key shared by all sensors
❌ No individual sensor tracking
❌ Anyone can register
```

### After (Sensor-Based)
```
API Key → Unique Sensor ID → One Sensor
✅ Each sensor has dedicated key
✅ Individual sensor tracking
✅ Registration requires email whitelist
✅ Admin validates each API key
```

## Key Features

### 1. Sensor-Based API Keys
- **Unique Sensor ID**: Each sensor gets a unique identifier (e.g., `HOSP001-TEMP-001`)
- **One Key Per Sensor**: No more sharing keys between sensors
- **Validation Required**: Admins must approve each API key before use
- **Truncated Display**: Keys show only first 12 characters in listings

### 2. Email Whitelist
- **Restricted Registration**: Only whitelisted emails can create accounts
- **Admin Management**: Admins can add/remove emails from whitelist
- **Clear Messaging**: Users see why registration fails if not whitelisted

### 3. Enhanced Security
- **Sensor ID Validation**: Each request checks sensor_id matches API key
- **Data Size Limits**: Custom data limited to 1MB
- **Better Tracking**: Last used timestamps, audit trail
- **Data Minimization**: Only essential data exposed

## Quick Setup (New Installation)

1. **Run Database Migration**
   ```bash
   docker compose exec backend alembic upgrade head
   ```

2. **Add Admin Email to Whitelist** (via Python shell)
   ```python
   from app.database import SessionLocal
   from app.models import AllowedEmail
   
   db = SessionLocal()
   db.add(AllowedEmail(email="admin@example.com"))
   db.commit()
   ```

3. **Create API Key** (via Admin UI)
   - Login as admin
   - Go to "API Keys Management"
   - Click "Generate New API Key"
   - Enter sensor ID (e.g., `HOSP001-TEMP-001`)
   - Select hospital
   - Add description
   - Click "Validate" to enable the key

## Quick Setup (Existing Installation)

1. **Run Migration**
   ```bash
   docker compose exec backend alembic upgrade head
   ```

2. **Run Post-Migration Script**
   ```bash
   docker compose exec backend python migrate_to_sensor_keys.py
   ```
   This will:
   - Add existing user emails to whitelist
   - Optionally update existing API keys with sensor IDs

3. **Notify Users**
   - Inform users about email whitelist
   - Update sensor devices with new API requirements

## Using the System

### For Admins

**Add Email to Whitelist:**
1. Login to admin dashboard
2. Go to "Email Whitelist Management"
3. Click "Add Email to Whitelist"
4. Enter email address
5. Click "Add Email"

**Create API Key:**
1. Go to "API Keys Management"
2. Click "Generate New API Key"
3. Enter unique sensor ID
4. Select hospital
5. Add description (optional)
6. Click "Generate Key"
7. **Copy the key immediately** (shown only once)
8. Click "Validate" to enable the key

**View API Keys:**
- See all sensors with their validation status
- Hospital names displayed (not IDs)
- Keys shown truncated for security
- Last used timestamps visible

### For Sensor Operators

**Send Sensor Data:**
```python
import requests

API_URL = "http://your-server:8000/api/sensors/data"
API_KEY = "sk_your_generated_api_key_here"
SENSOR_ID = "HOSP001-TEMP-001"  # Must match your API key

data = {
    "sensor_id": SENSOR_ID,  # Required: Must match API key
    "temperature": 22.5,
    "humidity": 45.2,
    "air_quality": 85,
    "custom_data": {  # Optional, max 1MB
        "location": "Ward A"
    }
}

headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

response = requests.post(API_URL, json=data, headers=headers)
```

**Common Errors:**

- **403 - "API key pending admin validation"**: Contact admin to validate your key
- **403 - "Sensor ID mismatch"**: Your sensor_id doesn't match the API key's sensor_id
- **413 - "custom_data exceeds maximum size"**: Reduce custom_data to under 1MB
- **401 - "Invalid API key"**: Check your API key is correct

### For Users

**Register:**
1. Go to registration page
2. **Ensure your email is whitelisted** (contact admin if needed)
3. Fill in username, email, password
4. Submit registration
5. Wait for admin to assign role

**Error Messages:**
- "Email not authorized for registration": Contact admin to add your email

## Naming Convention for Sensor IDs

Recommended format: `{HOSPITAL_CODE}-{SENSOR_TYPE}-{NUMBER}`

Examples:
- `NGH-TEMP-001` - North General Hospital, Temperature sensor #1
- `NGH-TEMP-002` - North General Hospital, Temperature sensor #2
- `NGH-HUM-001` - North General Hospital, Humidity sensor #1
- `SRH-AQ-001` - South Regional Hospital, Air Quality sensor #1

## Security Best Practices

1. **API Keys**: Never hardcode, use environment variables
2. **HTTPS**: Always use HTTPS in production
3. **Key Rotation**: Regularly rotate API keys
4. **Monitor Usage**: Check last_used timestamps for anomalies
5. **Revoke Unused**: Revoke keys for decommissioned sensors
6. **Unique IDs**: Always use unique, descriptive sensor IDs
7. **Data Limits**: Respect the 1MB custom_data limit
8. **Validation**: Always validate API keys after creation

## Troubleshooting

**Migration fails:**
- Check database connectivity
- Ensure no existing sensor_id values conflict
- Review migration logs

**Can't register:**
- Verify email is in whitelist
- Check for typos in email address
- Contact admin to add email

**Sensor data rejected:**
- Verify API key is validated
- Check sensor_id matches API key
- Ensure custom_data < 1MB
- Verify API key is active

**API key not working:**
- Check if validated by admin
- Verify key hasn't been revoked
- Ensure correct X-API-Key header

## Support

For issues or questions:
1. Check IMPLEMENTATION_SUMMARY.md for details
2. Review README.md for full documentation
3. Check SECURITY.md for security guidelines
4. Open an issue on GitHub

## Migration Timeline

**Week 1:**
- Run database migration
- Add existing emails to whitelist
- Update/regenerate API keys

**Week 2:**
- Update sensor devices with new requirements
- Test sensor data ingestion
- Validate all sensors working

**Week 3:**
- Monitor for issues
- Revoke legacy keys if needed
- Full production deployment

## Resources

- **IMPLEMENTATION_SUMMARY.md**: Detailed technical changes
- **README.md**: Complete documentation
- **SECURITY.md**: Security guidelines
- **migrate_to_sensor_keys.py**: Migration helper script
- **test_sensor_api.py**: Validation tests
