from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    SQL_HOST: str
    SQL_USER: str
    SQL_PASSWORD: str
    SQL_DATABASE: str
    OPEN_AI_API: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
