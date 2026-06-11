from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    cors_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CAREER_PAGES_PATH = DATA_DIR / "career_pages.json"
JOB_CATEGORIES_PATH = DATA_DIR / "job_categories.json"
COMPANY_PARSER_PATH = DATA_DIR / "company_parser.json"

settings = Settings()
