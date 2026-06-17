import os
from typing import Optional

class Settings:
    PROJECT_NAME: str = "琴行教务管理系统"
    VERSION: str = "1.0.0"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "music-school-secret-key-2024")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./music_school.db"
    )

settings = Settings()
