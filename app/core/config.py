from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_EXPIRE_MINUTES: int = 480
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    FRONTEND_URL: str
    ALGORITHM: str = "HS256"
    HF_TOKEN: str=""

    class Config:
        env_file = ".env"


settings = Settings()
