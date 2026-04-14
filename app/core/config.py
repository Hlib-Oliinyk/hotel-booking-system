from pathlib import Path
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).parent.parent.parent.resolve()

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file = ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_URL: str = ""

    SECRET_KEY: str
    ALGORITHM: str

    @model_validator(mode="after")
    def build_db_url(self):
        self.DB_URL = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_NAME}"
        return self


settings = Settings()