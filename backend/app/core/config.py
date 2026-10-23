import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "AICTE SETU — Institutional Compliance Monitoring System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./aicte_setu.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production-aicte-setu")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

settings = Settings()
