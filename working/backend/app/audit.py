"""
Audit logging utility for tracking all system actions

This module provides functions to log user and system actions for security,
compliance, and debugging purposes. All audit logging is non-blocking and 
failures in logging do not affect the primary operation.
"""
from sqlalchemy.orm import Session
from fastapi import Request
from typing import Optional, Dict, Any
from app.models import AuditLog, User
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def log_action(
    db: Session,
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    user: Optional[User] = None,
    request: Optional[Request] = None,
    status: str = "success"
) -> Optional[AuditLog]:
    """
    Core function to log an action to the audit log.
    
    Args:
        db: Database session
        action: Action name (e.g., "user_login", "region_create")
        resource_type: Type of resource affected (e.g., "user", "region", "hospital")
        resource_id: ID of the affected resource
        details: Additional context as a dictionary
        user: User performing the action (optional for system actions)
        request: FastAPI request object to extract IP and user agent
        status: Status of the action ("success" or "failure")
    
    Returns:
        AuditLog object if successful, None if logging failed
    """
    try:
        # Extract IP address and user agent from request
        ip_address = None
        user_agent = None
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
        
        # Create audit log entry
        audit_log = AuditLog(
            user_id=user.id if user else None,
            username=user.username if user else None,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.utcnow(),
            status=status
        )
        
        db.add(audit_log)
        db.commit()
        
        return audit_log
    except Exception as e:
        # Log the error but don't fail the main operation
        logger.error(f"Failed to create audit log: {str(e)}")
        try:
            db.rollback()
        except:
            pass
        return None


def log_login(
    db: Session,
    user: User,
    request: Request,
    status: str = "success",
    failure_reason: Optional[str] = None
) -> Optional[AuditLog]:
    """Log user login attempt"""
    details = {}
    if failure_reason:
        details["reason"] = failure_reason
    
    return log_action(
        db=db,
        action="user_login",
        resource_type="user",
        resource_id=user.id if user else None,
        details=details if details else None,
        user=user if status == "success" else None,
        request=request,
        status=status
    )


def log_logout(
    db: Session,
    user: User,
    request: Request
) -> Optional[AuditLog]:
    """Log user logout"""
    return log_action(
        db=db,
        action="user_logout",
        resource_type="user",
        resource_id=user.id,
        user=user,
        request=request
    )


def log_register(
    db: Session,
    user: User,
    request: Request
) -> Optional[AuditLog]:
    """Log user registration"""
    return log_action(
        db=db,
        action="user_register",
        resource_type="user",
        resource_id=user.id,
        details={"email": user.email},
        user=user,
        request=request
    )


def log_role_change(
    db: Session,
    target_user: User,
    old_role: int,
    new_role: int,
    admin_user: User,
    request: Request
) -> Optional[AuditLog]:
    """Log user role change"""
    return log_action(
        db=db,
        action="role_update",
        resource_type="user",
        resource_id=target_user.id,
        details={
            "target_username": target_user.username,
            "old_role": old_role,
            "new_role": new_role
        },
        user=admin_user,
        request=request
    )


def log_user_assignment(
    db: Session,
    target_user: User,
    region_id: Optional[int],
    hospital_id: Optional[int],
    admin_user: User,
    request: Request
) -> Optional[AuditLog]:
    """Log user assignment to region/hospital"""
    return log_action(
        db=db,
        action="user_assign",
        resource_type="user",
        resource_id=target_user.id,
        details={
            "target_username": target_user.username,
            "region_id": region_id,
            "hospital_id": hospital_id
        },
        user=admin_user,
        request=request
    )


def log_api_key_action(
    db: Session,
    action_type: str,  # "create", "validate", "revoke"
    api_key_id: int,
    sensor_id: str,
    hospital_id: int,
    admin_user: User,
    request: Request
) -> Optional[AuditLog]:
    """Log API key management actions"""
    return log_action(
        db=db,
        action=f"api_key_{action_type}",
        resource_type="api_key",
        resource_id=api_key_id,
        details={
            "sensor_id": sensor_id,
            "hospital_id": hospital_id
        },
        user=admin_user,
        request=request
    )


def log_2fa_action(
    db: Session,
    action_type: str,  # "enable" or "disable"
    user: User,
    request: Request
) -> Optional[AuditLog]:
    """Log 2FA enable/disable"""
    return log_action(
        db=db,
        action=f"2fa_{action_type}",
        resource_type="user",
        resource_id=user.id,
        user=user,
        request=request
    )


def log_resource_action(
    db: Session,
    action_type: str,  # "create", "update", "delete"
    resource_type: str,  # "region", "hospital", "allowed_email"
    resource_id: int,
    resource_name: Optional[str],
    admin_user: User,
    request: Request,
    additional_details: Optional[Dict[str, Any]] = None
) -> Optional[AuditLog]:
    """Log CRUD actions on resources (regions, hospitals, etc.)"""
    details = {"name": resource_name} if resource_name else {}
    if additional_details:
        details.update(additional_details)
    
    return log_action(
        db=db,
        action=f"{resource_type}_{action_type}",
        resource_type=resource_type,
        resource_id=resource_id,
        details=details if details else None,
        user=admin_user,
        request=request
    )


def log_sensor_data(
    db: Session,
    sensor_id: str,
    hospital_id: int,
    data_count: int = 1
) -> Optional[AuditLog]:
    """
    Log sensor data ingestion (with sampling to avoid too many logs).
    
    Note: This is called less frequently than actual data ingestion to avoid
    overwhelming the audit log. Consider logging only every Nth reading or
    implementing a separate sensor activity log.
    """
    return log_action(
        db=db,
        action="sensor_data_ingest",
        resource_type="sensor_data",
        resource_id=sensor_id,
        details={
            "hospital_id": hospital_id,
            "count": data_count
        },
        user=None,  # System action
        request=None,
        status="success"
    )
