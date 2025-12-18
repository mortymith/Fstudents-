from pydantic_settings import BaseSettings
from pydantic import Field

__all__ = ["settings"]


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Inventory Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = Field('your-super-secret-key-here-minimum-32-chars',min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 7 days
    REFRESH_SECRET_KEY: str = Field('another-super-secret-key-here-minimum-32-chars', min_length=32)
    
    # Session
    SESSION_TTL_HOURS: int = 24  # 24 hours
    SESSION_INACTIVITY_MINUTES: int = 30  # 30 minutes
    MAX_SESSIONS_PER_USER: int = 15
    
    # Password reset
    PASSWORD_RESET_EXPIRY_MINUTES: int = 60  # 1 hour


    POSTGRES_USER: str = Field("app_user")
    POSTGRES_PASSWORD: str = Field("pass12345")
    POSTGRES_DB: str = Field("app_db")
    POSTGRES_PORT: int = Field(5432)
    POSTGRES_HOST: str = Field("localhost")
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    REDIS_USERNAME: str = Field("app_user")
    REDIS_PASSWORD: str = Field("pass12345")
    REDIS_PORT: int = Field(6379)
    REDIS_HOST: str = Field("localhost")
    REDIS_DB: str = Field("0")

    PGADMIN_EMAIL: str = Field("admin@yourdomain.com")
    PGADMIN_PASSWORD: str = Field("pass12345")
    REDIS_COMMANDER_USER: str = Field("admin")
    REDIS_COMMANDER_PASSWORD: str = Field("pass12345")
    REDIS_POOL_SIZE: int = 10

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Email (for password reset)
    SMTP_HOST: str | None = None
    SMTP_PORT: int | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAIL_FROM: str | None = None

    

    class Config:
        extra='allow'
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def postgresql_url(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_USERNAME}:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()
