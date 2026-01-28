"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional, Dict, Any


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class User2FAVerify(BaseModel):
    """Schema for 2FA verification"""
    username: str
    totp_code: str = Field(..., min_length=6, max_length=6)


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_2fa_enabled: bool
    created_at: datetime
    last_login: Optional[datetime]
    role: int
    region_id: Optional[int] = None
    hospital_id: Optional[int] = None
    
    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    """Schema for updating user role"""
    role: int = Field(..., ge=1, le=4)


class UserAssignment(BaseModel):
    """Schema for assigning users to regions/hospitals"""
    region_id: Optional[int] = None
    hospital_id: Optional[int] = None


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    requires_2fa: bool = False


class Token2FAResponse(BaseModel):
    """Schema for 2FA token response"""
    requires_2fa: bool = True
    message: str = "2FA code required"


class Enable2FAResponse(BaseModel):
    """Schema for enable 2FA response"""
    qr_code: str
    secret: str
    message: str = "Scan QR code with your authenticator app"


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str


# Region Schemas
class RegionCreate(BaseModel):
    """Schema for creating a region"""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=20)


class RegionUpdate(BaseModel):
    """Schema for updating a region"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    code: Optional[str] = Field(None, min_length=1, max_length=20)


class RegionResponse(BaseModel):
    """Schema for region response"""
    id: int
    name: str
    code: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Hospital Schemas
class HospitalCreate(BaseModel):
    """Schema for creating a hospital"""
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=50)
    region_id: int
    address: Optional[str] = None


class HospitalUpdate(BaseModel):
    """Schema for updating a hospital"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    region_id: Optional[int] = None
    address: Optional[str] = None


class HospitalResponse(BaseModel):
    """Schema for hospital response"""
    id: int
    name: str
    code: str
    region_id: int
    address: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Sensor Data Schemas
class SensorDataCreate(BaseModel):
    """Schema for creating sensor data"""
    sensor_id: str = Field(..., min_length=1, max_length=100)
    timestamp: Optional[datetime] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    air_quality: Optional[float] = None
    custom_data: Optional[Dict[str, Any]] = None


class SensorDataResponse(BaseModel):
    """Schema for sensor data response"""
    id: int
    hospital_id: int
    sensor_id: str
    timestamp: datetime
    temperature: Optional[float]
    humidity: Optional[float]
    air_quality: Optional[float]
    data_json: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


# API Key Schemas
class APIKeyCreate(BaseModel):
    """Schema for creating an API key"""
    sensor_id: str = Field(..., min_length=1, max_length=100)
    hospital_id: int
    description: Optional[str] = None


class APIKeyResponse(BaseModel):
    """Schema for API key response"""
    id: int
    key: str
    sensor_id: str
    hospital_id: int
    description: Optional[str]
    is_active: bool
    is_validated: bool
    created_at: datetime
    last_used: Optional[datetime]
    
    class Config:
        from_attributes = True


class DataItemCreate(BaseModel):
    """Schema for creating data item"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)


class DataItemResponse(BaseModel):
    """Schema for data item response"""
    id: int
    user_id: int
    title: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Sensor Overview Schemas
class SensorOverviewResponse(BaseModel):
    """Schema for sensor overview with statistics"""
    sensor_id: str
    hospital_id: int
    hospital_name: str
    region_id: int
    region_name: str
    last_reading_timestamp: datetime
    temperature: Optional[float]
    humidity: Optional[float]
    air_quality: Optional[float]
    is_active: bool
    total_readings: int


class SensorStatsResponse(BaseModel):
    """Schema for system-wide sensor statistics"""
    total_sensors: int
    active_sensors: int
    inactive_sensors: int
    readings_last_24h: int


# Allowed Email Schemas
class AllowedEmailCreate(BaseModel):
    """Schema for adding an email to the whitelist"""
    email: EmailStr


class AllowedEmailResponse(BaseModel):
    """Schema for allowed email response"""
    id: int
    email: str
    created_at: datetime
    created_by: Optional[int]
    
    class Config:
        from_attributes = True
