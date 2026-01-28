"""
Admin router for managing users, regions, hospitals, and API keys
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, Region, Hospital, APIKey, SensorData, AllowedEmail
from app.schemas import (
    UserResponse, UserRoleUpdate, UserAssignment,
    RegionCreate, RegionResponse, RegionUpdate,
    HospitalCreate, HospitalResponse, HospitalUpdate,
    APIKeyCreate, APIKeyResponse, MessageResponse,
    SensorOverviewResponse, SensorStatsResponse, SensorDataResponse,
    AllowedEmailCreate, AllowedEmailResponse
)
from app.dependencies import require_admin
import secrets

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.post("/users/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user role (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent admin from changing their own role
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own role"
        )
    
    user.role = role_update.role
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/users/{user_id}/assign", response_model=UserResponse)
async def assign_user(
    user_id: int,
    assignment: UserAssignment,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Assign user to region/hospital (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate region exists if provided
    if assignment.region_id:
        region = db.query(Region).filter(Region.id == assignment.region_id).first()
        if not region:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Region not found"
            )
    
    # Validate hospital exists if provided
    if assignment.hospital_id:
        hospital = db.query(Hospital).filter(Hospital.id == assignment.hospital_id).first()
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found"
            )
        # Ensure hospital belongs to the region if region is also being set
        if assignment.region_id and hospital.region_id != assignment.region_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hospital does not belong to the specified region"
            )
    
    user.region_id = assignment.region_id
    user.hospital_id = assignment.hospital_id
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    role: Optional[int] = None,
    region_id: Optional[int] = None,
    hospital_id: Optional[int] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all users with optional filters (admin only)"""
    query = db.query(User)
    
    if role is not None:
        query = query.filter(User.role == role)
    if region_id is not None:
        query = query.filter(User.region_id == region_id)
    if hospital_id is not None:
        query = query.filter(User.hospital_id == hospital_id)
    
    users = query.all()
    return users


@router.get("/regions", response_model=List[RegionResponse])
async def list_regions(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all regions (admin only)"""
    regions = db.query(Region).all()
    return regions


@router.post("/regions", response_model=RegionResponse, status_code=status.HTTP_201_CREATED)
async def create_region(
    region_data: RegionCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new region (admin only)"""
    # Check if region with same name or code exists
    existing = db.query(Region).filter(
        (Region.name == region_data.name) | (Region.code == region_data.code)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Region with this name or code already exists"
        )
    
    region = Region(
        name=region_data.name,
        code=region_data.code
    )
    db.add(region)
    db.commit()
    db.refresh(region)
    
    return region


@router.get("/hospitals", response_model=List[HospitalResponse])
async def list_hospitals(
    region_id: Optional[int] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all hospitals with optional region filter (admin only)"""
    query = db.query(Hospital)
    
    if region_id is not None:
        query = query.filter(Hospital.region_id == region_id)
    
    hospitals = query.all()
    return hospitals


@router.post("/hospitals", response_model=HospitalResponse, status_code=status.HTTP_201_CREATED)
async def create_hospital(
    hospital_data: HospitalCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new hospital (admin only)"""
    # Check if region exists
    region = db.query(Region).filter(Region.id == hospital_data.region_id).first()
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Region not found"
        )
    
    # Check if hospital with same name or code exists
    existing = db.query(Hospital).filter(
        (Hospital.name == hospital_data.name) | (Hospital.code == hospital_data.code)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hospital with this name or code already exists"
        )
    
    hospital = Hospital(
        name=hospital_data.name,
        code=hospital_data.code,
        region_id=hospital_data.region_id,
        address=hospital_data.address
    )
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    
    return hospital


@router.post("/api-keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    api_key_data: APIKeyCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Generate API key for sensor (admin only)"""
    # Check if hospital exists
    hospital = db.query(Hospital).filter(Hospital.id == api_key_data.hospital_id).first()
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    # Check if sensor_id is unique
    existing_key = db.query(APIKey).filter(APIKey.sensor_id == api_key_data.sensor_id).first()
    if existing_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API key for sensor '{api_key_data.sensor_id}' already exists"
        )
    
    # Generate secure API key
    api_key_value = f"sk_{secrets.token_urlsafe(32)}"
    
    api_key = APIKey(
        key=api_key_value,
        sensor_id=api_key_data.sensor_id,
        hospital_id=api_key_data.hospital_id,
        description=api_key_data.description,
        is_validated=False  # Admin must validate after creation
    )
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    return api_key


@router.delete("/api-keys/{key_id}", response_model=MessageResponse)
async def revoke_api_key(
    key_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Revoke API key (admin only)"""
    api_key = db.query(APIKey).filter(APIKey.id == key_id).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    api_key.is_active = False
    db.commit()
    
    return MessageResponse(message="API key revoked successfully")


@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    hospital_id: Optional[int] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all API keys with optional hospital filter (admin only)"""
    query = db.query(APIKey)
    
    if hospital_id is not None:
        query = query.filter(APIKey.hospital_id == hospital_id)
    
    api_keys = query.all()
    return api_keys


@router.put("/regions/{region_id}", response_model=RegionResponse)
async def update_region(
    region_id: int,
    region_data: RegionUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update region details (admin only)"""
    region = db.query(Region).filter(Region.id == region_id).first()
    
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Region not found"
        )
    
    # Check if new name or code conflicts with existing regions
    if region_data.name and region_data.name != region.name:
        existing = db.query(Region).filter(Region.name == region_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Region with this name already exists"
            )
        region.name = region_data.name
    
    if region_data.code and region_data.code != region.code:
        existing = db.query(Region).filter(Region.code == region_data.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Region with this code already exists"
            )
        region.code = region_data.code
    
    db.commit()
    db.refresh(region)
    
    return region


@router.delete("/regions/{region_id}", response_model=MessageResponse)
async def delete_region(
    region_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Delete region (admin only) - only if no hospitals or users assigned"""
    region = db.query(Region).filter(Region.id == region_id).first()
    
    if not region:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Region not found"
        )
    
    # Check if region has hospitals
    hospitals_count = db.query(Hospital).filter(Hospital.region_id == region_id).count()
    if hospitals_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete region with {hospitals_count} hospitals. Remove hospitals first."
        )
    
    # Check if region has users
    users_count = db.query(User).filter(User.region_id == region_id).count()
    if users_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete region with {users_count} users. Reassign users first."
        )
    
    db.delete(region)
    db.commit()
    
    return MessageResponse(message="Region deleted successfully")


@router.put("/hospitals/{hospital_id}", response_model=HospitalResponse)
async def update_hospital(
    hospital_id: int,
    hospital_data: HospitalUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update hospital details (admin only)"""
    hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
    
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    # Check if new name or code conflicts with existing hospitals
    if hospital_data.name and hospital_data.name != hospital.name:
        existing = db.query(Hospital).filter(Hospital.name == hospital_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hospital with this name already exists"
            )
        hospital.name = hospital_data.name
    
    if hospital_data.code and hospital_data.code != hospital.code:
        existing = db.query(Hospital).filter(Hospital.code == hospital_data.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hospital with this code already exists"
            )
        hospital.code = hospital_data.code
    
    if hospital_data.region_id is not None:
        # Verify new region exists
        region = db.query(Region).filter(Region.id == hospital_data.region_id).first()
        if not region:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Region not found"
            )
        hospital.region_id = hospital_data.region_id
    
    if hospital_data.address is not None:
        hospital.address = hospital_data.address
    
    db.commit()
    db.refresh(hospital)
    
    return hospital


@router.get("/sensors/overview", response_model=List[SensorOverviewResponse])
async def get_sensors_overview(
    hospital_id: Optional[int] = None,
    region_id: Optional[int] = None,
    sensor_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get overview of all sensors with latest readings and status (admin only)"""
    # Get distinct sensors with their latest reading and total count in one query
    subquery = db.query(
        SensorData.sensor_id,
        SensorData.hospital_id,
        func.max(SensorData.timestamp).label('latest_timestamp'),
        func.count(SensorData.id).label('total_readings')
    ).group_by(SensorData.sensor_id, SensorData.hospital_id)
    
    if hospital_id:
        subquery = subquery.filter(SensorData.hospital_id == hospital_id)
    if sensor_id:
        subquery = subquery.filter(SensorData.sensor_id.like(f"%{sensor_id}%"))
    
    subquery = subquery.subquery()
    
    # Join to get full sensor data
    query = db.query(
        SensorData,
        subquery.c.total_readings
    ).join(
        subquery,
        (SensorData.sensor_id == subquery.c.sensor_id) &
        (SensorData.hospital_id == subquery.c.hospital_id) &
        (SensorData.timestamp == subquery.c.latest_timestamp)
    ).join(Hospital)
    
    if region_id:
        query = query.filter(Hospital.region_id == region_id)
    
    # Add pagination
    results = query.order_by(SensorData.timestamp.desc()).offset(offset).limit(limit).all()
    
    # Build overview response
    overview = []
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    
    for reading, total_readings in results:
        # Determine if sensor is active (data in last hour)
        is_active = reading.timestamp >= one_hour_ago
        
        overview.append(SensorOverviewResponse(
            sensor_id=reading.sensor_id,
            hospital_id=reading.hospital_id,
            hospital_name=reading.hospital.name,
            region_id=reading.hospital.region_id,
            region_name=reading.hospital.region.name,
            last_reading_timestamp=reading.timestamp,
            temperature=reading.temperature,
            humidity=reading.humidity,
            air_quality=reading.air_quality,
            is_active=is_active,
            total_readings=total_readings
        ))
    
    return overview


@router.get("/sensors/{sensor_id}/history", response_model=List[SensorDataResponse])
async def get_sensor_history(
    sensor_id: str,
    hospital_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get detailed history for a specific sensor (admin only)"""
    query = db.query(SensorData).filter(SensorData.sensor_id == sensor_id)
    
    if hospital_id:
        query = query.filter(SensorData.hospital_id == hospital_id)
    
    history = query.order_by(SensorData.timestamp.desc()).offset(offset).limit(limit).all()
    
    return history


@router.get("/sensors/stats", response_model=SensorStatsResponse)
async def get_sensor_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get system-wide sensor statistics (admin only)"""
    # Total unique sensors
    total_sensors = db.query(
        func.count(func.distinct(SensorData.sensor_id))
    ).scalar() or 0
    
    # Total readings in last 24 hours
    twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
    readings_24h = db.query(func.count(SensorData.id)).filter(
        SensorData.timestamp >= twenty_four_hours_ago
    ).scalar() or 0
    
    # Active sensors (data in last hour)
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    active_sensors = db.query(
        func.count(func.distinct(SensorData.sensor_id))
    ).filter(
        SensorData.timestamp >= one_hour_ago
    ).scalar() or 0
    
    # Inactive sensors - sensors with latest reading older than 24 hours
    # Use a subquery to get the latest timestamp for each sensor
    latest_per_sensor = db.query(
        SensorData.sensor_id,
        func.max(SensorData.timestamp).label('latest_timestamp')
    ).group_by(SensorData.sensor_id).subquery()
    
    inactive_count = db.query(func.count()).select_from(latest_per_sensor).filter(
        latest_per_sensor.c.latest_timestamp < twenty_four_hours_ago
    ).scalar() or 0
    
    return SensorStatsResponse(
        total_sensors=total_sensors,
        active_sensors=active_sensors,
        inactive_sensors=inactive_count,
        readings_last_24h=readings_24h
    )


@router.put("/api-keys/{key_id}/validate", response_model=APIKeyResponse)
async def validate_api_key(
    key_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Validate/approve an API key (admin only)"""
    api_key = db.query(APIKey).filter(APIKey.id == key_id).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    api_key.is_validated = True
    db.commit()
    db.refresh(api_key)
    
    return api_key


@router.post("/allowed-emails", response_model=AllowedEmailResponse, status_code=status.HTTP_201_CREATED)
async def add_allowed_email(
    email_data: AllowedEmailCreate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Add email to whitelist (admin only)"""
    # Check if email already exists
    existing = db.query(AllowedEmail).filter(AllowedEmail.email == email_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already in whitelist"
        )
    
    allowed_email = AllowedEmail(
        email=email_data.email,
        created_by=current_user.id
    )
    db.add(allowed_email)
    db.commit()
    db.refresh(allowed_email)
    
    return allowed_email


@router.get("/allowed-emails", response_model=List[AllowedEmailResponse])
async def list_allowed_emails(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all whitelisted emails (admin only)"""
    emails = db.query(AllowedEmail).all()
    return emails


@router.delete("/allowed-emails/{email_id}", response_model=MessageResponse)
async def delete_allowed_email(
    email_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Remove email from whitelist (admin only)"""
    allowed_email = db.query(AllowedEmail).filter(AllowedEmail.id == email_id).first()
    
    if not allowed_email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found in whitelist"
        )
    
    db.delete(allowed_email)
    db.commit()
    
    return MessageResponse(message="Email removed from whitelist successfully")
