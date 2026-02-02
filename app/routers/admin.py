"""
Admin Router - Handles admin dashboard and user management.

This router provides endpoints for:
1. Getting global statistics
2. Managing users
3. Viewing platform analytics

**Note:** Only users with role="admin" can access these endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Article, QuizAttempt
from app.utils.logger import logger
from pydantic import BaseModel
from datetime import datetime


# ============================================================
# SCHEMAS
# ============================================================

class GlobalStatsResponse(BaseModel):
    """Response schema for global statistics."""
    total_users: int
    total_articles: int
    total_summaries: int
    total_translations: int
    total_quizzes_generated: int
    total_quiz_attempts: int
    average_quiz_score: float


class UserAdminResponse(BaseModel):
    """Response schema for user admin view."""
    id: int
    username: str
    email: str
    role: str
    created_at: datetime
    article_count: int
    quiz_attempts: int
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Response schema for user list."""
    users: List[UserAdminResponse]
    total: int


class UserRoleUpdateRequest(BaseModel):
    """Request schema for updating user role."""
    role: str  # "user" or "admin"


# ============================================================
# HELPER FUNCTION
# ============================================================

async def verify_admin(current_user: User):
    """Verify that the current user has admin role."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Access denied. Admin privileges required."
        )
    return current_user


# ============================================================
# ROUTER SETUP
# ============================================================

router = APIRouter()


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/stats", response_model=GlobalStatsResponse)
async def get_global_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get global platform statistics.
    
    **Requires:** Admin role
    
    **Returns:**
    - Total number of users
    - Total articles processed
    - Breakdown by action type (summaries, translations, quizzes)
    - Quiz attempt statistics
    """
    await verify_admin(current_user)
    
    logger.info(f"Admin {current_user.username} fetching global stats")
    
    try:
        # Count total users
        users_result = await db.execute(select(func.count(User.id)))
        total_users = users_result.scalar()
        
        # Count total articles
        articles_result = await db.execute(select(func.count(Article.id)))
        total_articles = articles_result.scalar()
        
        # Count by action type
        summaries_result = await db.execute(
            select(func.count(Article.id)).where(Article.action == "summary")
        )
        total_summaries = summaries_result.scalar()
        
        translations_result = await db.execute(
            select(func.count(Article.id)).where(Article.action == "translation")
        )
        total_translations = translations_result.scalar()
        
        quizzes_result = await db.execute(
            select(func.count(Article.id)).where(Article.action == "quiz")
        )
        total_quizzes = quizzes_result.scalar()
        
        # Count quiz attempts
        attempts_result = await db.execute(select(func.count(QuizAttempt.id)))
        total_attempts = attempts_result.scalar()
        
        # Calculate average quiz score
        avg_score_result = await db.execute(select(func.avg(QuizAttempt.score)))
        average_score = avg_score_result.scalar() or 0
        
        return GlobalStatsResponse(
            total_users=total_users,
            total_articles=total_articles,
            total_summaries=total_summaries,
            total_translations=total_translations,
            total_quizzes_generated=total_quizzes,
            total_quiz_attempts=total_attempts,
            average_quiz_score=round(average_score, 2)
        )
        
    except Exception as e:
        logger.error(f"Error fetching global stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch stats: {str(e)}")


@router.get("/users", response_model=UserListResponse)
async def get_all_users(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of all users with their activity statistics.
    
    **Requires:** Admin role
    
    **Query parameters:**
    - `limit`: Maximum users to return (default: 50)
    - `offset`: Number of users to skip (pagination)
    """
    await verify_admin(current_user)
    
    logger.info(f"Admin {current_user.username} fetching user list")
    
    try:
        # Get users
        result = await db.execute(
            select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
        )
        users = result.scalars().all()
        
        # Build response with article and quiz counts
        users_with_stats = []
        for user in users:
            # Count articles
            article_count_result = await db.execute(
                select(func.count(Article.id)).where(Article.user_id == user.id)
            )
            article_count = article_count_result.scalar()
            
            # Count quiz attempts
            quiz_count_result = await db.execute(
                select(func.count(QuizAttempt.id)).where(QuizAttempt.user_id == user.id)
            )
            quiz_count = quiz_count_result.scalar()
            
            users_with_stats.append(UserAdminResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                created_at=user.created_at,
                article_count=article_count,
                quiz_attempts=quiz_count
            ))
        
        # Get total count
        total_result = await db.execute(select(func.count(User.id)))
        total = total_result.scalar()
        
        return UserListResponse(
            users=users_with_stats,
            total=total
        )
        
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch users: {str(e)}")


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: int,
    request: UserRoleUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a user's role (promote to admin or demote to user).
    
    **Requires:** Admin role
    
    **Valid roles:** "user", "admin"
    """
    await verify_admin(current_user)
    
    # Prevent self-demotion
    if user_id == current_user.id and request.role != "admin":
        raise HTTPException(
            status_code=400,
            detail="You cannot demote yourself"
        )
    
    logger.info(f"Admin {current_user.username} updating role for user {user_id} to {request.role}")
    
    try:
        # Find user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate role
        if request.role not in ["user", "admin"]:
            raise HTTPException(status_code=400, detail="Invalid role. Must be 'user' or 'admin'")
        
        # Update role
        user.role = request.role
        await db.commit()
        
        return {
            "message": f"User role updated successfully",
            "user_id": user_id,
            "new_role": request.role
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user role: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update role: {str(e)}")


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a user account.
    
    **Requires:** Admin role
    
    **Warning:** This will also delete all user's articles and quiz attempts.
    """
    await verify_admin(current_user)
    
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete your own account"
        )
    
    logger.info(f"Admin {current_user.username} deleting user {user_id}")
    
    try:
        # Find user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Delete user (cascade will delete articles and quiz attempts)
        await db.delete(user)
        await db.commit()
        
        return {
            "message": "User deleted successfully",
            "user_id": user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")
