"""
Database models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    totp_secret = Column(String(255), nullable=True)
    is_2fa_enabled = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    
    # RBAC fields
    role = Column(Integer, default=1, nullable=False)  # 1=Pending, 2=Admin, 3=Region Admin, 4=Hospital User
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=True)
    
    # Relationships
    data_items = relationship("DataItem", back_populates="user", cascade="all, delete-orphan")
    region = relationship("Region", back_populates="users")
    hospital = relationship("Hospital", back_populates="users")


class Region(Base):
    """Region model for geographical organization"""
    __tablename__ = "regions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    hospitals = relationship("Hospital", back_populates="region")
    users = relationship("User", back_populates="region")


class Hospital(Base):
    """Hospital model"""
    __tablename__ = "hospitals"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    region_id = Column(Integer, ForeignKey("regions.id"), nullable=False)
    address = Column(String(500), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    map_zoom = Column(Integer, default=13, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    region = relationship("Region", back_populates="hospitals")
    users = relationship("User", back_populates="hospital")
    sensor_data = relationship("SensorData", back_populates="hospital")


class SensorData(Base):
    """Sensor data model for storing IoT device readings"""
    __tablename__ = "sensor_data"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    sensor_id = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    air_quality = Column(Float, nullable=True)
    data_json = Column(JSON, nullable=False)  # Store all sensor data as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    hospital = relationship("Hospital", back_populates="sensor_data")


class APIKey(Base):
    """API key model for sensor authentication"""
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    sensor_id = Column(String(100), unique=True, nullable=False, index=True)
    hospital_id = Column(Integer, ForeignKey("hospitals.id"), nullable=False)
    description = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_validated = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)


class AllowedEmail(Base):
    """Email whitelist for registration"""
    __tablename__ = "allowed_emails"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)


class DataItem(Base):
    """Example data model to demonstrate API functionality"""
    __tablename__ = "data_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    user = relationship("User", back_populates="data_items")


class AuditLog(Base):
    """Audit log model for tracking all system actions"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Nullable for system actions
    username = Column(String(50), nullable=True, index=True)  # Denormalized for faster queries
    action = Column(String(100), nullable=False, index=True)  # e.g., "user_login", "user_register"
    resource_type = Column(String(50), nullable=True, index=True)  # e.g., "user", "region", "hospital"
    resource_id = Column(String(100), nullable=True)  # ID of affected resource
    details = Column(JSON, nullable=True)  # Additional context about the action
    ip_address = Column(String(50), nullable=True)  # User's IP address
    user_agent = Column(String(500), nullable=True)  # Browser/client info
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    status = Column(String(20), default="success", nullable=False)  # success/failure
    
    # Note: Consider implementing log retention policy to archive/delete old logs
    # Recommendation: Keep logs for 90 days in active table, archive older logs
