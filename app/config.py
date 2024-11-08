from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    BROKER_URL: str
    BACKEND_URL: Optional[str] = None
    # DATABASE_URL: str FOR DB IF WE WILL USE IT
    MODEL_PATH: str

    class Config:
        env_file = ".env"


settings = Settings()  # type: ignore
