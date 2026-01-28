"""
FastAPI dependencies for authentication and authorization
"""
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, APIKey
from app.auth import verify_token
from typing import Optional
from datetime import datetime

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = verify_token(token, token_type="access")
    
    if payload is None:
        raise credentials_exception
    
    username: Optional[str] = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user (can add additional checks here)"""
    return current_user


def require_role(min_role: int):
    """Decorator to require minimum role level"""
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role < min_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker


async def require_admin(current_user: User = Depends(get_current_active_user)):
    """Require admin role (role 2)"""
    if current_user.role != 2:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def require_region_admin_or_admin(current_user: User = Depends(get_current_active_user)):
    """Require region admin or higher"""
    if current_user.role < 2 or current_user.role > 3:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Region admin or admin access required"
        )
    return current_user


async def verify_api_key(
    x_api_key: str = Header(...),
    db: Session = Depends(get_db)
) -> APIKey:
    """Verify API key for sensor endpoints"""
    api_key = db.query(APIKey).filter(
        APIKey.key == x_api_key,
        APIKey.is_active == True
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Check if API key is validated by admin
    if not api_key.is_validated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="API key pending admin validation"
        )
    
    # Update last used timestamp
    api_key.last_used = datetime.utcnow()
    db.commit()
    
    return api_key
