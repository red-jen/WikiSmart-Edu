"""
Content Router - Handles Wikipedia and PDF content extraction.

This router provides endpoints for:
1. Extracting content from Wikipedia URLs
2. Uploading and extracting text from PDF files
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.services.wikipedia_service import WikipediaService
from app.services.pdf_service import PDFService
from app.utils.logger import logger
from pydantic import BaseModel, Field, validator
from urllib.parse import urlparse


# ============================================================
# SCHEMAS (Request/Response models for this router)
# ============================================================

class WikipediaRequest(BaseModel):
    """Request schema for Wikipedia content extraction."""
    url: str = Field(..., description="Wikipedia article URL")
    language: str = Field(default="fr", description="Language code (fr, en, ar, es)")
    
    @validator("url")
    def validate_wikipedia_url(cls, v):
        """Ensure URL is from Wikipedia."""
        parsed = urlparse(v)
        if not parsed.netloc.endswith("wikipedia.org"):
            raise ValueError("URL must be from Wikipedia (e.g., https://fr.wikipedia.org/wiki/...)")
        return v


class ContentResponse(BaseModel):
    """Response schema for extracted content."""
    title: str
    content: str
    sections: dict = {}
    source: str  # "wikipedia" or "pdf"
    character_count: int
    

# ============================================================
# ROUTER SETUP
# ============================================================

router = APIRouter()

# Initialize services
wikipedia_service = WikipediaService()
pdf_service = PDFService()


# ============================================================
# ENDPOINTS
# ============================================================

@router.post("/wikipedia", response_model=ContentResponse)
async def extract_wikipedia_content(
    request: WikipediaRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Extract content from a Wikipedia article URL.
    
    **How it works:**
    1. User provides a Wikipedia URL (e.g., https://fr.wikipedia.org/wiki/Python)
    2. We parse the URL to get the article title
    3. We fetch the article content from Wikipedia
    4. We return the title, content, and sections
    
    **Example request:**
    ```json
    {
        "url": "https://fr.wikipedia.org/wiki/Intelligence_artificielle",
        "language": "fr"
    }
    ```
    """
    logger.info(f"User {current_user.username} extracting Wikipedia content: {request.url}")
    
    try:
        # Use the Wikipedia service to extract content
        result = wikipedia_service.extract_article_content(
            url=request.url,
            language=request.language
        )
        
        return ContentResponse(
            title=result["title"],
            content=result["full_content"],
            sections=result.get("sections", {}),
            source="wikipedia",
            character_count=len(result["full_content"])
        )
        
    except Exception as e:
        logger.error(f"Error extracting Wikipedia content: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pdf", response_model=ContentResponse)
async def extract_pdf_content(
    file: UploadFile = File(..., description="PDF file to extract text from"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Extract text content from an uploaded PDF file.
    
    **How it works:**
    1. User uploads a PDF file
    2. We read and parse the PDF
    3. We extract text from all pages
    4. We return the extracted content
    
    **Accepts:** PDF files only (max size depends on server config)
    """
    logger.info(f"User {current_user.username} uploading PDF: {file.filename}")
    
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted. Please upload a .pdf file."
        )
    
    try:
        # Read file content
        pdf_bytes = await file.read()
        
        # Use PDF service to extract content
        result = pdf_service.extract_text_from_bytes(
            pdf_bytes=pdf_bytes,
            filename=file.filename
        )
        
        return ContentResponse(
            title=result["filename"].replace(".pdf", ""),
            content=result["full_content"],
            sections=result.get("pages", {}),
            source="pdf",
            character_count=result["character_count"]
        )
        
    except Exception as e:
        logger.error(f"Error extracting PDF content: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
