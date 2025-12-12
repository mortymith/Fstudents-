from pydantic_settings import BaseSettings
from pydantic import Field

__all__ = ["settings"]


class Settings(BaseSettings):
    POSTGRES_USER: str = Field("app_user")
    POSTGRES_PASSWORD: str = Field("pass12345")
    POSTGRES_DB: str = Field("app_db")
    POSTGRES_PORT: int = Field(5432)
    POSTGRES_HOST: str = Field("localhost")

    REDIS_USERNAME: str = Field("app_user")
    REDIS_PASSWORD: str = Field("pass12345")
    REDIS_PORT: int = Field(6379)
    REDIS_HOST: str = Field("localhost")
    REDIS_DB: str = Field("0")

    PGADMIN_EMAIL: str = Field("admin@yourdomain.com")
    PGADMIN_PASSWORD: str = Field("pass12345")
    REDIS_COMMANDER_USER: str = Field("admin")
    REDIS_COMMANDER_PASSWORD: str = Field("pass12345")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def postgresql_url(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_USERNAME}:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


settings = Settings()
