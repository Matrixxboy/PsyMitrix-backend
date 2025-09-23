# core/config.py
# Configuration settings for the application.
# This file loads environment variables and defines configuration parameters.

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # --- Project Info ---
    PROJECT_NAME: str = "PsyMitrix AI Backend"
    PROJECT_VERSION: str = "1.0.0"

    # --- Database ---
    MONGO_URI: str
    QDRANT_HOST: str
    QDRANT_PORT: int = 6333
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "user_embeddings"

    # --- Security ---
    ENCRYPTION_KEY: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

# Point-wise comment: Create a single instance of the settings
settings = Settings()
