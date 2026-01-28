"""
Data router for protected endpoints that demonstrate API functionality
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, DataItem
from app.schemas import DataItemCreate, DataItemResponse
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/api/data", tags=["Data"])


@router.get("/", response_model=List[DataItemResponse])
async def get_data(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all data items for the current user"""
    data_items = db.query(DataItem).filter(DataItem.user_id == current_user.id).all()
    return data_items


@router.post("/", response_model=DataItemResponse, status_code=status.HTTP_201_CREATED)
async def create_data(
    data: DataItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new data item"""
    db_item = DataItem(
        user_id=current_user.id,
        title=data.title,
        content=data.content
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=DataItemResponse)
async def get_data_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific data item"""
    item = db.query(DataItem).filter(
        DataItem.id == item_id,
        DataItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data item not found"
        )
    
    return item


@router.delete("/{item_id}")
async def delete_data_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a data item"""
    item = db.query(DataItem).filter(
        DataItem.id == item_id,
        DataItem.user_id == current_user.id
    ).first()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Data item not found"
        )
    
    db.delete(item)
    db.commit()
    
    return {"message": "Data item deleted successfully"}
