# from pydantic_settings import BaseSettings
from typing import Optional

# BaseSettings as parent class 
class Settings():
    # Database
    DATABASE_URL: str
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()