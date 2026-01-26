from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings using Pydantic Settings."""
    
    # Database Configuration
    DATABASE_URL: str
    
    # JWT Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Groq API Configuration (for summaries)
    GROQ_API_KEY: str
    GROQ_MODEL: str = "mixtral-8x7b-32768"
    GROQ_TEMPERATURE: float = 0.3
    GROQ_MAX_TOKENS: int = 1000
    
    # Google Gemini API Configuration (for translation and quiz)
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-pro"
    GEMINI_TEMPERATURE: float = 0.5
    GEMINI_MAX_TOKENS: int = 2000
    
    # Wikipedia Configuration
    WIKIPEDIA_USER_AGENT: str = "WikiSmartEdu/1.0 (contact: youremail@example.com)"
    
    # Application Settings
    APP_NAME: str = "WikiSmart-Edu"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into list."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
