from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import init_db
from app.utils.exceptions import WikiSmartException
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting WikiSmart-Edu application")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down WikiSmart-Edu application")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Plateforme éducative intelligente pour l'apprentissage autonome",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(WikiSmartException)
async def wikismart_exception_handler(request, exc: WikiSmartException):
    """Handle custom WikiSmart exceptions."""
    logger.error(f"WikiSmart Exception: {exc.detail}", extra={
        "status_code": exc.status_code,
        "path": request.url.path
    })
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", extra={
        "path": request.url.path,
        "exception_type": type(exc).__name__
    }, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to WikiSmart-Edu API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


# Import and include routers
from app.routers import auth, content, llm, articles, quiz, export, admin

# Authentication endpoints
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

# Content extraction endpoints (Wikipedia & PDF)
app.include_router(content.router, prefix="/api/content", tags=["Content Extraction"])

# LLM processing endpoints (Summary, Translation, Quiz Generation)
app.include_router(llm.router, prefix="/api/llm", tags=["LLM Processing"])

# Article history endpoints
app.include_router(articles.router, prefix="/api/articles", tags=["Articles"])

# Quiz endpoints (submit answers, history)
app.include_router(quiz.router, prefix="/api/quiz", tags=["Quiz"])

# Export endpoints (PDF, TXT)
app.include_router(export.router, prefix="/api/export", tags=["Export"])

# Admin endpoints (requires admin role)
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])

