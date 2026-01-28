"""
Region admin router for managing users and hospitals within their region
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Hospital, SensorData
from app.schemas import (
    UserResponse, UserAssignment,
    HospitalResponse, SensorDataResponse
)
from app.dependencies import require_region_admin_or_admin

router = APIRouter(prefix="/api/region", tags=["Region Admin"])


@router.get("/users", response_model=List[UserResponse])
async def list_region_users(
    current_user: User = Depends(require_region_admin_or_admin),
    db: Session = Depends(get_db)
):
    """List users in my region (region admin only)"""
    if current_user.role == 2:
        # Admin can see all users
        users = db.query(User).all()
    else:
        # Region admin can only see users in their region
        if not current_user.region_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Region admin must be assigned to a region"
            )
        users = db.query(User).filter(User.region_id == current_user.region_id).all()
    
    return users


@router.post("/users/{user_id}/assign-hospital", response_model=UserResponse)
async def assign_user_to_hospital(
    user_id: int,
    assignment: UserAssignment,
    current_user: User = Depends(require_region_admin_or_admin),
    db: Session = Depends(get_db)
):
    """Assign user to hospital in my region (region admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Region admin can only assign users within their region
    if current_user.role == 3:
        if not current_user.region_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Region admin must be assigned to a region"
            )
        
        if user.region_id != current_user.region_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only assign users within your region"
            )
    
    # Validate hospital if provided
    if assignment.hospital_id:
        hospital = db.query(Hospital).filter(Hospital.id == assignment.hospital_id).first()
        if not hospital:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hospital not found"
            )
        
        # Ensure hospital is in the region admin's region
        if current_user.role == 3 and hospital.region_id != current_user.region_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Hospital is not in your region"
            )
        
        user.hospital_id = assignment.hospital_id
    
    db.commit()
    db.refresh(user)
    
    return user


@router.get("/hospitals", response_model=List[HospitalResponse])
async def list_region_hospitals(
    current_user: User = Depends(require_region_admin_or_admin),
    db: Session = Depends(get_db)
):
    """List hospitals in my region (region admin only)"""
    if current_user.role == 2:
        # Admin can see all hospitals
        hospitals = db.query(Hospital).all()
    else:
        # Region admin can only see hospitals in their region
        if not current_user.region_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Region admin must be assigned to a region"
            )
        hospitals = db.query(Hospital).filter(Hospital.region_id == current_user.region_id).all()
    
    return hospitals


@router.get("/sensor-data", response_model=List[SensorDataResponse])
async def get_region_sensor_data(
    limit: int = 100,
    current_user: User = Depends(require_region_admin_or_admin),
    db: Session = Depends(get_db)
):
    """Get sensor data for my region (region admin only)"""
    if current_user.role == 2:
        # Admin can see all sensor data
        sensor_data = db.query(SensorData).order_by(SensorData.timestamp.desc()).limit(limit).all()
    else:
        # Region admin can only see sensor data from hospitals in their region
        if not current_user.region_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Region admin must be assigned to a region"
            )
        
        sensor_data = db.query(SensorData).join(Hospital).filter(
            Hospital.region_id == current_user.region_id
        ).order_by(SensorData.timestamp.desc()).limit(limit).all()
    
    return sensor_data
