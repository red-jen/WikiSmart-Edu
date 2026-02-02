"""
Quiz Router - Handles quiz submission and history.

This router provides endpoints for:
1. Submitting quiz answers and getting scores
2. Viewing quiz attempt history
3. Getting quiz statistics
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Article, QuizAttempt
from app.utils.logger import logger
from pydantic import BaseModel, Field
from datetime import datetime


# ============================================================
# SCHEMAS
# ============================================================

class QuizAnswer(BaseModel):
    """Schema for a single quiz answer."""
    question_index: int
    user_answer: str


class QuizSubmitRequest(BaseModel):
    """Request schema for quiz submission."""
    article_id: int = Field(..., description="ID of the article the quiz is based on")
    answers: List[QuizAnswer] = Field(..., description="List of user's answers")
    correct_answers: List[str] = Field(..., description="List of correct answers for comparison")


class QuizSubmitResponse(BaseModel):
    """Response schema for quiz submission."""
    attempt_id: int
    score: float
    total_questions: int
    correct_answers: int
    percentage: float
    details: List[dict]  # Per-question results


class QuizAttemptResponse(BaseModel):
    """Response schema for a quiz attempt."""
    id: int
    article_id: int
    article_title: Optional[str] = None
    score: float
    total_questions: int
    correct_answers: int
    percentage: float
    submitted_at: datetime
    
    class Config:
        from_attributes = True


class QuizHistoryResponse(BaseModel):
    """Response schema for quiz history."""
    attempts: List[QuizAttemptResponse]
    total_attempts: int
    average_score: float
    best_score: float


class QuizStatsResponse(BaseModel):
    """Response schema for quiz statistics."""
    total_quizzes_taken: int
    average_score: float
    best_score: float
    worst_score: float
    total_questions_answered: int
    total_correct_answers: int


# ============================================================
# ROUTER SETUP
# ============================================================

router = APIRouter()


# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/submit", response_model=QuizSubmitResponse)
async def submit_quiz(
    request: QuizSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit quiz answers and get the score.
    
    **How it works:**
    1. User submits their answers along with correct answers
    2. We compare and calculate the score
    3. We save the attempt to the database
    4. We return detailed results
    
    **Example request:**
    ```json
    {
        "article_id": 1,
        "answers": [
            {"question_index": 0, "user_answer": "Python"},
            {"question_index": 1, "user_answer": "1991"}
        ],
        "correct_answers": ["Python", "1991"]
    }
    ```
    """
    logger.info(f"User {current_user.username} submitting quiz for article {request.article_id}")
    
    try:
        # Verify article exists and belongs to user
        result = await db.execute(
            select(Article).where(
                Article.id == request.article_id,
                Article.user_id == current_user.id
            )
        )
        article = result.scalar_one_or_none()
        
        if not article:
            raise HTTPException(
                status_code=404,
                detail="Article not found or you don't have permission"
            )
        
        # Calculate score
        total_questions = len(request.correct_answers)
        correct_count = 0
        details = []
        
        for i, answer in enumerate(request.answers):
            is_correct = False
            if i < len(request.correct_answers):
                # Case-insensitive comparison
                is_correct = answer.user_answer.strip().lower() == request.correct_answers[i].strip().lower()
                if is_correct:
                    correct_count += 1
            
            details.append({
                "question_index": i,
                "user_answer": answer.user_answer,
                "correct_answer": request.correct_answers[i] if i < len(request.correct_answers) else None,
                "is_correct": is_correct
            })
        
        # Calculate percentage
        percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        # Save quiz attempt
        quiz_attempt = QuizAttempt(
            user_id=current_user.id,
            article_id=request.article_id,
            score=percentage,
            total_questions=total_questions,
            correct_answers=correct_count
        )
        
        db.add(quiz_attempt)
        await db.commit()
        await db.refresh(quiz_attempt)
        
        logger.info(f"Quiz submitted: {correct_count}/{total_questions} ({percentage:.1f}%)")
        
        return QuizSubmitResponse(
            attempt_id=quiz_attempt.id,
            score=percentage,
            total_questions=total_questions,
            correct_answers=correct_count,
            percentage=percentage,
            details=details
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting quiz: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to submit quiz: {str(e)}")


@router.get("/history", response_model=QuizHistoryResponse)
async def get_quiz_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's quiz attempt history.
    
    **Returns:**
    - List of quiz attempts with scores
    - Total number of attempts
    - Average and best scores
    """
    logger.info(f"User {current_user.username} fetching quiz history")
    
    try:
        # Get quiz attempts with article titles
        query = select(QuizAttempt).where(
            QuizAttempt.user_id == current_user.id
        ).order_by(QuizAttempt.submitted_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        attempts = result.scalars().all()
        
        # Get article titles for each attempt
        attempts_with_titles = []
        for attempt in attempts:
            article_result = await db.execute(
                select(Article.title).where(Article.id == attempt.article_id)
            )
            article_title = article_result.scalar_one_or_none()
            
            attempts_with_titles.append(QuizAttemptResponse(
                id=attempt.id,
                article_id=attempt.article_id,
                article_title=article_title,
                score=attempt.score,
                total_questions=attempt.total_questions,
                correct_answers=attempt.correct_answers,
                percentage=attempt.score,
                submitted_at=attempt.submitted_at
            ))
        
        # Calculate statistics
        all_attempts_result = await db.execute(
            select(QuizAttempt.score).where(QuizAttempt.user_id == current_user.id)
        )
        all_scores = [row[0] for row in all_attempts_result.fetchall()]
        
        total_attempts = len(all_scores)
        average_score = sum(all_scores) / total_attempts if total_attempts > 0 else 0
        best_score = max(all_scores) if all_scores else 0
        
        return QuizHistoryResponse(
            attempts=attempts_with_titles,
            total_attempts=total_attempts,
            average_score=round(average_score, 2),
            best_score=best_score
        )
        
    except Exception as e:
        logger.error(f"Error fetching quiz history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch quiz history: {str(e)}")


@router.get("/stats", response_model=QuizStatsResponse)
async def get_quiz_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's overall quiz statistics.
    
    **Returns:**
    - Total quizzes taken
    - Average, best, and worst scores
    - Total questions answered
    - Total correct answers
    """
    logger.info(f"User {current_user.username} fetching quiz stats")
    
    try:
        # Get all quiz attempts for the user
        result = await db.execute(
            select(QuizAttempt).where(QuizAttempt.user_id == current_user.id)
        )
        attempts = result.scalars().all()
        
        if not attempts:
            return QuizStatsResponse(
                total_quizzes_taken=0,
                average_score=0,
                best_score=0,
                worst_score=0,
                total_questions_answered=0,
                total_correct_answers=0
            )
        
        scores = [a.score for a in attempts]
        total_questions = sum(a.total_questions for a in attempts)
        total_correct = sum(a.correct_answers for a in attempts)
        
        return QuizStatsResponse(
            total_quizzes_taken=len(attempts),
            average_score=round(sum(scores) / len(scores), 2),
            best_score=max(scores),
            worst_score=min(scores),
            total_questions_answered=total_questions,
            total_correct_answers=total_correct
        )
        
    except Exception as e:
        logger.error(f"Error fetching quiz stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch quiz stats: {str(e)}")
