"""
Sensor router for ingesting and retrieving sensor data
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models import User, Hospital, SensorData, APIKey
from app.schemas import SensorDataCreate, SensorDataResponse
from app.dependencies import verify_api_key, get_current_active_user
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/sensors", tags=["Sensors"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/data", response_model=SensorDataResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
async def ingest_sensor_data(
    request: Request,
    sensor_data: SensorDataCreate,
    api_key: APIKey = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """Ingest sensor data from Orange Pi or other IoT devices"""
    # Validate sensor_id matches the API key's sensor_id
    if sensor_data.sensor_id != api_key.sensor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Sensor ID mismatch. This API key is registered for sensor '{api_key.sensor_id}'"
        )
    
    # Build data_json from all provided fields
    data_json = {}
    
    if sensor_data.temperature is not None:
        data_json["temperature"] = sensor_data.temperature
    if sensor_data.humidity is not None:
        data_json["humidity"] = sensor_data.humidity
    if sensor_data.air_quality is not None:
        data_json["air_quality"] = sensor_data.air_quality
    if sensor_data.custom_data:
        # Validate custom_data size (max 1MB when serialized)
        import json
        custom_data_size = len(json.dumps(sensor_data.custom_data))
        if custom_data_size > 1048576:  # 1MB
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="custom_data exceeds maximum size of 1MB"
            )
        data_json.update(sensor_data.custom_data)
    
    # Create sensor data record
    db_sensor_data = SensorData(
        hospital_id=api_key.hospital_id,
        sensor_id=sensor_data.sensor_id,
        timestamp=sensor_data.timestamp or datetime.utcnow(),
        temperature=sensor_data.temperature,
        humidity=sensor_data.humidity,
        air_quality=sensor_data.air_quality,
        data_json=data_json
    )
    
    db.add(db_sensor_data)
    
    # Update API key last_used timestamp
    api_key.last_used = datetime.utcnow()
    
    db.commit()
    db.refresh(db_sensor_data)
    
    return db_sensor_data


@router.get("/data", response_model=List[SensorDataResponse])
async def get_sensor_data(
    hospital_id: Optional[int] = None,
    sensor_id: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get sensor data with role-based filtering"""
    query = db.query(SensorData)
    
    # Apply role-based filtering
    if current_user.role == 1:
        # Pending users cannot access sensor data
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pending users do not have access to sensor data"
        )
    elif current_user.role == 4:
        # Hospital users can only see their hospital's data
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hospital user must be assigned to a hospital"
            )
        query = query.filter(SensorData.hospital_id == current_user.hospital_id)
    elif current_user.role == 3:
        # Region admins can see data from hospitals in their region
        if not current_user.region_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Region admin must be assigned to a region"
            )
        query = query.join(Hospital).filter(Hospital.region_id == current_user.region_id)
    # Role 2 (Admin) can see all data - no filter needed
    
    # Apply additional filters if provided
    if hospital_id is not None:
        # Verify user has access to this hospital
        if current_user.role == 4 and hospital_id != current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your hospital's data"
            )
        elif current_user.role == 3:
            hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
            if hospital and hospital.region_id != current_user.region_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only access hospitals in your region"
                )
        query = query.filter(SensorData.hospital_id == hospital_id)
    
    if sensor_id is not None:
        query = query.filter(SensorData.sensor_id == sensor_id)
    
    sensor_data = query.order_by(SensorData.timestamp.desc()).limit(limit).all()
    return sensor_data


@router.get("/data/{hospital_id}", response_model=List[SensorDataResponse])
async def get_hospital_sensor_data(
    hospital_id: int,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get sensor data for specific hospital"""
    # Check if user has access to this hospital
    if current_user.role == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pending users do not have access to sensor data"
        )
    elif current_user.role == 4:
        if current_user.hospital_id != hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access your hospital's data"
            )
    elif current_user.role == 3:
        hospital = db.query(Hospital).filter(Hospital.id == hospital_id).first()
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found"
            )
        if hospital.region_id != current_user.region_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only access hospitals in your region"
            )
    
    sensor_data = db.query(SensorData).filter(
        SensorData.hospital_id == hospital_id
    ).order_by(SensorData.timestamp.desc()).limit(limit).all()
    
    return sensor_data


@router.get("/latest", response_model=List[SensorDataResponse])
async def get_latest_sensor_readings(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get latest sensor readings (one per sensor) with role-based filtering"""
    if current_user.role == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pending users do not have access to sensor data"
        )
    
    # Build base query with role filtering
    query = db.query(SensorData)
    
    if current_user.role == 4:
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hospital user must be assigned to a hospital"
            )
        query = query.filter(SensorData.hospital_id == current_user.hospital_id)
    elif current_user.role == 3:
        if not current_user.region_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Region admin must be assigned to a region"
            )
        query = query.join(Hospital).filter(Hospital.region_id == current_user.region_id)
    
    # Get distinct sensor_ids and their latest readings
    # Note: This is a simplified approach. For production, you might want to use window functions
    latest_data = []
    sensor_ids = set()
    
    all_data = query.order_by(SensorData.timestamp.desc()).all()
    for data in all_data:
        key = f"{data.hospital_id}_{data.sensor_id}"
        if key not in sensor_ids:
            sensor_ids.add(key)
            latest_data.append(data)
    
    return latest_data[:100]  # Limit to 100 latest unique sensors
