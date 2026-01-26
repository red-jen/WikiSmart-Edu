"""Authentication dependencies for FastAPI."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import User
from app.schemas import TokenData
from app.utils.security import decode_access_token
from app.utils.exceptions import UnauthorizedException, ForbiddenException

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Args:
        token: JWT access token
        db: Database session
    
    Returns:
        User: Authenticated user object
    
    Raises:
        UnauthorizedException: If token is invalid or user not found
    """
    # Decode token
    payload = decode_access_token(token)
    
    if payload is None:
        raise UnauthorizedException("Could not validate credentials")
    
    username: str = payload.get("sub")
    user_id: int = payload.get("user_id")
    
    if username is None or user_id is None:
        raise UnauthorizedException("Could not validate credentials")
    
    # Get user from database
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise UnauthorizedException("User not found")
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User: Active user object
    
    Raises:
        ForbiddenException: If user is inactive (for future use)
    """
    # For now, all users are active
    # Add is_active field to User model if needed in future
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Require admin role for accessing endpoint.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        User: Admin user object
    
    Raises:
        ForbiddenException: If user is not admin
    """
    if current_user.role != "admin":
        raise ForbiddenException("Admin access required")
    
    return current_user
