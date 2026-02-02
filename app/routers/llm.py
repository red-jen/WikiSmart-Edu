"""
LLM Router - Handles AI-powered text processing.

This router provides endpoints for:
1. Summarizing content (using Groq)
2. Translating content (using Google Gemini)
3. Generating quizzes (using Google Gemini)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Literal, List

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User, Article
from app.services.llm_service import LLMService
from app.utils.logger import logger
from pydantic import BaseModel, Field


# ============================================================
# SCHEMAS (Request/Response models)
# ============================================================

class SummarizeRequest(BaseModel):
    """Request schema for summarization."""
    content: str = Field(..., min_length=100, description="Text content to summarize")
    summary_type: Literal["short", "medium"] = Field(
        default="medium",
        description="Summary length: 'short' (~150 words) or 'medium' (~300 words)"
    )


class SummarizeResponse(BaseModel):
    """Response schema for summarization."""
    original_length: int
    summary: str
    summary_length: int
    summary_type: str


class TranslateRequest(BaseModel):
    """Request schema for translation."""
    content: str = Field(..., min_length=10, description="Text content to translate")
    target_language: Literal["FR", "EN", "AR", "ES"] = Field(
        ...,
        description="Target language code: FR (French), EN (English), AR (Arabic), ES (Spanish)"
    )


class TranslateResponse(BaseModel):
    """Response schema for translation."""
    original_content: str
    translated_content: str
    target_language: str


class QuizQuestion(BaseModel):
    """Schema for a single quiz question."""
    question: str
    type: Literal["mcq", "open"]  # Multiple choice or open-ended
    options: Optional[List[str]] = None  # For MCQ questions
    correct_answer: str


class GenerateQuizRequest(BaseModel):
    """Request schema for quiz generation."""
    content: str = Field(..., min_length=200, description="Text content to generate quiz from")
    num_mcq: int = Field(default=5, ge=1, le=10, description="Number of MCQ questions (1-10)")
    num_open: int = Field(default=3, ge=0, le=5, description="Number of open questions (0-5)")


class GenerateQuizResponse(BaseModel):
    """Response schema for quiz generation."""
    questions: List[QuizQuestion]
    total_questions: int
    source_length: int


# ============================================================
# ROUTER SETUP
# ============================================================

router = APIRouter()

# Initialize LLM service
llm_service = LLMService()


# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/summarize", response_model=SummarizeResponse)
async def summarize_content(
    request: SummarizeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a summary of the provided content using Groq LLM.
    
    **How it works:**
    1. User provides text content (from Wikipedia or PDF)
    2. We send it to Groq API with a summarization prompt
    3. Groq returns a concise summary
    
    **Summary types:**
    - `short`: ~150 words, key points only
    - `medium`: ~300 words, more detailed
    
    **Example request:**
    ```json
    {
        "content": "Long article text here...",
        "summary_type": "short"
    }
    ```
    """
    logger.info(f"User {current_user.username} requesting {request.summary_type} summary")
    
    try:
        # Generate summary using Groq
        summary = await llm_service.generate_summary(
            content=request.content,
            summary_type=request.summary_type
        )
        
        return SummarizeResponse(
            original_length=len(request.content),
            summary=summary,
            summary_length=len(summary),
            summary_type=request.summary_type
        )
        
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")


@router.post("/translate", response_model=TranslateResponse)
async def translate_content(
    request: TranslateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Translate content to a target language using Google Gemini.
    
    **Supported languages:**
    - `FR`: French (Français)
    - `EN`: English
    - `AR`: Arabic (العربية)
    - `ES`: Spanish (Español)
    
    **Example request:**
    ```json
    {
        "content": "L'intelligence artificielle est...",
        "target_language": "EN"
    }
    ```
    """
    logger.info(f"User {current_user.username} translating to {request.target_language}")
    
    try:
        # Translate using Gemini
        translated = await llm_service.translate_text(
            content=request.content,
            target_language=request.target_language
        )
        
        return TranslateResponse(
            original_content=request.content[:500] + "..." if len(request.content) > 500 else request.content,
            translated_content=translated,
            target_language=request.target_language
        )
        
    except Exception as e:
        logger.error(f"Error translating content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to translate: {str(e)}")


@router.post("/quiz/generate", response_model=GenerateQuizResponse)
async def generate_quiz(
    request: GenerateQuizRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate a quiz from the provided content using Google Gemini.
    
    **Quiz format:**
    - MCQ questions: 4 options, 1 correct answer
    - Open questions: Short answer questions
    
    **Example request:**
    ```json
    {
        "content": "Article about Python programming...",
        "num_mcq": 5,
        "num_open": 2
    }
    ```
    
    **Example response:**
    ```json
    {
        "questions": [
            {
                "question": "What is Python?",
                "type": "mcq",
                "options": ["A language", "A snake", "A framework", "A database"],
                "correct_answer": "A language"
            },
            {
                "question": "Explain the main use of Python.",
                "type": "open",
                "correct_answer": "Python is used for web development, data science..."
            }
        ],
        "total_questions": 7
    }
    ```
    """
    logger.info(f"User {current_user.username} generating quiz: {request.num_mcq} MCQ, {request.num_open} open")
    
    try:
        # Generate quiz using Gemini
        quiz_data = await llm_service.generate_quiz(
            content=request.content,
            num_mcq=request.num_mcq,
            num_open=request.num_open
        )
        
        # Parse the quiz data into our response format
        questions = []
        for q in quiz_data.get("questions", []):
            questions.append(QuizQuestion(
                question=q["question"],
                type=q["type"],
                options=q.get("options"),
                correct_answer=q["correct_answer"]
            ))
        
        return GenerateQuizResponse(
            questions=questions,
            total_questions=len(questions),
            source_length=len(request.content)
        )
        
    except Exception as e:
        logger.error(f"Error generating quiz: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")
