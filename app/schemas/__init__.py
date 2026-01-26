from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Literal
from datetime import datetime
from urllib.parse import urlparse


class UserBase(BaseModel):
    """Base user schema."""
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration."""
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload."""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


class ArticleBase(BaseModel):
    """Base article schema."""
    url: Optional[str] = None
    title: str
    action: Literal["summary", "translation", "quiz"]
    language: Optional[str] = None
    summary_type: Optional[Literal["short", "medium"]] = None
    
    @validator("url")
    def validate_wikipedia_url(cls, v):
        """Validate that the URL is from Wikipedia."""
        if v is None:
            return v
        
        parsed = urlparse(v)
        if not parsed.netloc.endswith("wikipedia.org"):
            raise ValueError("URL must be from Wikipedia")
        
        return v


class ArticleCreate(ArticleBase):
    """Schema for creating an article."""
    pass


class ArticleResponse(ArticleBase):
    """Schema for article response."""
    id: int
    user_id: int
    content: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuizAttemptBase(BaseModel):
    """Base quiz attempt schema."""
    article_id: int
    score: float
    total_questions: int
    correct_answers: int


class QuizAttemptCreate(QuizAttemptBase):
    """Schema for creating a quiz attempt."""
    pass


class QuizAttemptResponse(QuizAttemptBase):
    """Schema for quiz attempt response."""
    id: int
    user_id: int
    submitted_at: datetime
    
    class Config:
        from_attributes = True


class SummaryRequest(BaseModel):
    """Schema for summary request."""
    content: str
    summary_type: Literal["short", "medium"] = "medium"


class TranslationRequest(BaseModel):
    """Schema for translation request."""
    content: str
    target_language: Literal["FR", "EN", "AR", "ES"]


class QuizGenerationRequest(BaseModel):
    """Schema for quiz generation request."""
    content: str
    num_mcq: int = Field(default=5, ge=1, le=20)
    num_open: int = Field(default=3, ge=1, le=10)
