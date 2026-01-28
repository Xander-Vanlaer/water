"""
Authentication router with login, registration, 2FA, and token management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, AllowedEmail
from app.schemas import (
    UserCreate, UserLogin, UserResponse, TokenResponse, 
    Token2FAResponse, User2FAVerify, Enable2FAResponse, MessageResponse,
    RefreshTokenRequest
)
from app.auth import (
    verify_password, get_password_hash, create_access_token, 
    create_refresh_token, verify_token, generate_totp_secret, 
    verify_totp, generate_qr_code
)
from app.dependencies import get_current_active_user
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
limiter = Limiter(key_func=get_remote_address)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if email is in whitelist (full email or domain)
    allowed_email = db.query(AllowedEmail).filter(AllowedEmail.email == user_data.email).first()
    
    # If not found by full email, check by domain
    if not allowed_email and '@' in user_data.email:
        email_parts = user_data.email.split('@')
        # Ensure valid email format (exactly one @ and content after it)
        if len(email_parts) == 2 and email_parts[1]:
            domain = '@' + email_parts[1]
            allowed_email = db.query(AllowedEmail).filter(AllowedEmail.email == domain).first()
    
    if not allowed_email:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not authorized for registration. Please contact an administrator."
        )
    
    # Check if username already exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login")
@limiter.limit("10/minute")
async def login(
    request: Request,
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Login with username and password"""
    # Find user
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        # Increment failed login attempts
        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account locked until {user.locked_until.isoformat()}"
        )
    
    # If 2FA is enabled, require 2FA verification
    if user.is_2fa_enabled:
        return Token2FAResponse()
    
    # Reset failed login attempts
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/verify-2fa", response_model=TokenResponse)
@limiter.limit("10/minute")
async def verify_2fa(
    request: Request,
    verify_data: User2FAVerify,
    db: Session = Depends(get_db)
):
    """Verify 2FA code and complete login"""
    user = db.query(User).filter(User.username == verify_data.username).first()
    
    if not user or not user.is_2fa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA not enabled for this user"
        )
    
    # Verify TOTP code
    if not verify_totp(user.totp_secret, verify_data.totp_code):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA code"
        )
    
    # Reset failed login attempts
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/enable-2fa", response_model=Enable2FAResponse)
async def enable_2fa(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enable 2FA for the current user"""
    if current_user.is_2fa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled"
        )
    
    # Generate TOTP secret
    secret = generate_totp_secret()
    
    # Generate QR code
    qr_code = generate_qr_code(current_user.username, secret)
    
    # Save secret (in production, you might want to encrypt this)
    current_user.totp_secret = secret
    current_user.is_2fa_enabled = True
    db.commit()
    
    return Enable2FAResponse(
        qr_code=qr_code,
        secret=secret
    )


@router.post("/disable-2fa", response_model=MessageResponse)
async def disable_2fa(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Disable 2FA for the current user"""
    if not current_user.is_2fa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is not enabled"
        )
    
    current_user.is_2fa_enabled = False
    current_user.totp_secret = None
    db.commit()
    
    return MessageResponse(message="2FA disabled successfully")


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    payload = verify_token(token_data.refresh_token, token_type="refresh")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    username = payload.get("sub")
    user = db.query(User).filter(User.username == username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Create new tokens
    access_token = create_access_token(data={"sub": user.username})
    new_refresh_token = create_refresh_token(data={"sub": user.username})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(current_user: User = Depends(get_current_active_user)):
    """Logout current user"""
    # In a production app, you might want to blacklist the token
    return MessageResponse(message="Logged out successfully")
