"""
Dashboard router for statistics and visualizations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any, List
from app.database import get_db
from app.models import User, Hospital, SensorData, Region
from app.schemas import SensorDataResponse
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get dashboard statistics filtered by role"""
    stats = {}
    
    if current_user.role == 1:
        # Pending users get limited stats
        stats = {
            "role": "pending",
            "message": "Your account is pending approval. Please contact an administrator.",
            "admin_email": "admin@example.com"
        }
    elif current_user.role == 2:
        # Admin gets all stats
        stats = {
            "role": "admin",
            "total_users": db.query(User).count(),
            "pending_users": db.query(User).filter(User.role == 1).count(),
            "total_regions": db.query(Region).count(),
            "total_hospitals": db.query(Hospital).count(),
            "total_sensor_readings": db.query(SensorData).count(),
            "recent_sensor_readings": db.query(SensorData).order_by(
                SensorData.timestamp.desc()
            ).limit(5).count()
        }
    elif current_user.role == 3:
        # Region admin gets region-specific stats
        if not current_user.region_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Region admin must be assigned to a region"
            )
        
        hospitals_in_region = db.query(Hospital).filter(
            Hospital.region_id == current_user.region_id
        ).all()
        hospital_ids = [h.id for h in hospitals_in_region]
        
        stats = {
            "role": "region_admin",
            "region_id": current_user.region_id,
            "total_hospitals": len(hospital_ids),
            "total_users_in_region": db.query(User).filter(
                User.region_id == current_user.region_id
            ).count(),
            "total_sensor_readings": db.query(SensorData).filter(
                SensorData.hospital_id.in_(hospital_ids)
            ).count() if hospital_ids else 0
        }
    elif current_user.role == 4:
        # Hospital user gets hospital-specific stats
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hospital user must be assigned to a hospital"
            )
        
        stats = {
            "role": "hospital_user",
            "hospital_id": current_user.hospital_id,
            "total_sensor_readings": db.query(SensorData).filter(
                SensorData.hospital_id == current_user.hospital_id
            ).count(),
            "unique_sensors": db.query(SensorData.sensor_id).filter(
                SensorData.hospital_id == current_user.hospital_id
            ).distinct().count()
        }
    
    return stats


@router.get("/sensor-data", response_model=List[SensorDataResponse])
async def get_dashboard_sensor_data(
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get sensor data for dashboard with role-based filtering"""
    if current_user.role == 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Pending users do not have access to sensor data"
        )
    
    query = db.query(SensorData)
    
    if current_user.role == 4:
        # Hospital users only see their hospital's data
        if not current_user.hospital_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hospital user must be assigned to a hospital"
            )
        query = query.filter(SensorData.hospital_id == current_user.hospital_id)
    elif current_user.role == 3:
        # Region admins see data from all hospitals in their region
        if not current_user.region_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Region admin must be assigned to a region"
            )
        query = query.join(Hospital).filter(Hospital.region_id == current_user.region_id)
    # Admin (role 2) sees all data - no filter
    
    sensor_data = query.order_by(SensorData.timestamp.desc()).limit(limit).all()
    return sensor_data
