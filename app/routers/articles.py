"""
Articles Router - Handles user's article history.

This router provides endpoints for:
1. Saving processed articles
2. Retrieving user's article history
3. Getting a specific article
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Literal

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Article
from app.utils.logger import logger
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================
# SCHEMAS
# ============================================================

class ArticleSaveRequest(BaseModel):
    """Request schema for saving an article."""
    url: Optional[str] = Field(None, description="Wikipedia URL (null for PDF)")
    title: str = Field(..., min_length=1, description="Article or PDF title")
    action: Literal["summary", "translation", "quiz"] = Field(..., description="Action performed")
    content: str = Field(..., description="Processed content (summary, translation, or quiz JSON)")
    language: Optional[str] = Field(None, description="Target language for translation")
    summary_type: Optional[Literal["short", "medium"]] = Field(None, description="Summary type")


class ArticleResponse(BaseModel):
    """Response schema for an article."""
    id: int
    url: Optional[str]
    title: str
    action: str
    content: Optional[str]
    language: Optional[str]
    summary_type: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """Response schema for article list."""
    articles: List[ArticleResponse]
    total: int


# ============================================================
# ROUTER SETUP
# ============================================================

router = APIRouter()


# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/", response_model=ArticleResponse)
async def save_article(
    request: ArticleSaveRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Save a processed article to user's history.
    
    **When to use:**
    - After summarizing content
    - After translating content
    - After generating a quiz
    
    This allows users to:
    - Track their learning history
    - Review past summaries/translations
    - Retake quizzes
    """
    logger.info(f"User {current_user.username} saving article: {request.title}")
    
    try:
        # Create new article record
        article = Article(
            user_id=current_user.id,
            url=request.url,
            title=request.title,
            action=request.action,
            content=request.content,
            language=request.language,
            summary_type=request.summary_type
        )
        
        db.add(article)
        await db.commit()
        await db.refresh(article)
        
        logger.info(f"Article saved with ID: {article.id}")
        
        return article
        
    except Exception as e:
        logger.error(f"Error saving article: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save article: {str(e)}")


@router.get("/", response_model=ArticleListResponse)
async def get_user_articles(
    action: Optional[Literal["summary", "translation", "quiz"]] = None,
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's article history.
    
    **Query parameters:**
    - `action`: Filter by action type (summary, translation, quiz)
    - `limit`: Maximum number of articles to return (default: 20)
    - `offset`: Number of articles to skip (for pagination)
    
    **Example:**
    - Get all: `GET /api/articles/`
    - Get summaries only: `GET /api/articles/?action=summary`
    - Pagination: `GET /api/articles/?limit=10&offset=20`
    """
    logger.info(f"User {current_user.username} fetching articles (action={action})")
    
    try:
        # Build query
        query = select(Article).where(Article.user_id == current_user.id)
        
        # Filter by action if specified
        if action:
            query = query.where(Article.action == action)
        
        # Order by newest first
        query = query.order_by(Article.created_at.desc())
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        # Execute query
        result = await db.execute(query)
        articles = result.scalars().all()
        
        # Get total count
        count_query = select(Article).where(Article.user_id == current_user.id)
        if action:
            count_query = count_query.where(Article.action == action)
        count_result = await db.execute(count_query)
        total = len(count_result.scalars().all())
        
        return ArticleListResponse(
            articles=articles,
            total=total
        )
        
    except Exception as e:
        logger.error(f"Error fetching articles: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch articles: {str(e)}")


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific article by ID.
    
    **Note:** Users can only access their own articles.
    """
    logger.info(f"User {current_user.username} fetching article ID: {article_id}")
    
    try:
        # Query for the article
        result = await db.execute(
            select(Article).where(
                Article.id == article_id,
                Article.user_id == current_user.id
            )
        )
        article = result.scalar_one_or_none()
        
        if not article:
            raise HTTPException(
                status_code=404,
                detail="Article not found or you don't have permission to access it"
            )
        
        return article
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching article: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch article: {str(e)}")


@router.delete("/{article_id}")
async def delete_article(
    article_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an article from user's history.
    
    **Note:** Users can only delete their own articles.
    """
    logger.info(f"User {current_user.username} deleting article ID: {article_id}")
    
    try:
        # Find the article
        result = await db.execute(
            select(Article).where(
                Article.id == article_id,
                Article.user_id == current_user.id
            )
        )
        article = result.scalar_one_or_none()
        
        if not article:
            raise HTTPException(
                status_code=404,
                detail="Article not found or you don't have permission to delete it"
            )
        
        # Delete the article
        await db.delete(article)
        await db.commit()
        
        return {"message": "Article deleted successfully", "id": article_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting article: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete article: {str(e)}")
