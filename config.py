"""
Application configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings"""
    
    # Application
    APP_NAME = "Solar System OAuth Server"
    APP_VERSION = "1.0.0 (In-Memory)"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM = "HS256"
    
    # OAuth2 Token expiration (in seconds)
    ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", "3600"))  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "30"))  # 30 days
    AUTHORIZATION_CODE_EXPIRE_MINUTES = 10  # 10 minutes
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Admin credentials (for initial setup)
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = "admin123"
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@example.com")
    
    # Fixed test client (for Railway and production deployment)
    TEST_CLIENT_ID = os.getenv("TEST_CLIENT_ID", "mcp_test_client")
    TEST_CLIENT_SECRET = os.getenv("TEST_CLIENT_SECRET", "test-secret-change-in-production")
    TEST_CLIENT_NAME = os.getenv("TEST_CLIENT_NAME", "MCP Test Client")
    TEST_CLIENT_REDIRECT_URIS = os.getenv(
        "TEST_CLIENT_REDIRECT_URIS",
        "http://localhost:3000/callback,http://127.0.0.1:3000/callback,http://localhost:8080/callback"
    ).split(",")


settings = Settings()
