from fastapi import HTTPException, status


class WikiSmartException(HTTPException):
    """Base exception for WikiSmart application."""
    
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "An error occurred",
        headers: dict = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class UnauthorizedException(WikiSmartException):
    """Exception for unauthorized access."""
    
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(WikiSmartException):
    """Exception for forbidden access."""
    
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundException(WikiSmartException):
    """Exception for resource not found."""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class BadRequestException(WikiSmartException):
    """Exception for bad requests."""
    
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ConflictException(WikiSmartException):
    """Exception for resource conflicts."""
    
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class LLMServiceException(WikiSmartException):
    """Exception for LLM service errors."""
    
    def __init__(self, detail: str = "LLM service error"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)


class WikipediaServiceException(WikiSmartException):
    """Exception for Wikipedia service errors."""
    
    def __init__(self, detail: str = "Wikipedia service error"):
        super().__init__(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=detail)
