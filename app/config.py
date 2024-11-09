from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    BROKER_URL: str
    BACKEND_URL: Optional[str] = None
    DATABASE_URL: str
    MODEL_PATH: str

    class Config:
        env_file = ".env"


settings = Settings()  # type: ignore
