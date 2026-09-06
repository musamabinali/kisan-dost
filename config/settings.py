from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator
from typing import Literal
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # LLM Provider
    llm_provider: Literal["openai", "gemini", "groq", "ollama"] = "openai"
    openai_api_key: str | None = None
    openai_base_url: str | None = None
    openai_model: str = "gpt-4o-mini"
    
    # For non-OpenAI providers
    gemini_api_key: str | None = None
    groq_api_key: str | None = None
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    # Agents SDK
    agents_sdk_tracing_enabled: bool = True
    agents_sdk_trace_export: Literal["console", "file", "otlp"] = "console"
    agents_sdk_trace_file: str = "traces/kisan_dost.jsonl"

    # Data
    data_dir: str = "data"
    use_real_apis: bool = False
    
    # External APIs
    open_meteo_timeout: int = 10
    amis_punjab_timeout: int = 15
    
    # Session
    session_backend: Literal["sqlite", "redis", "memory"] = "sqlite"
    session_db_path: str = "data/sessions.db"
    session_ttl_hours: int = 24
    
    # Safety
    max_pesticide_dosage_ml_per_acre: float = 2000.0
    banned_pesticides: list[str] = Field(default_factory=lambda: [
        "endosulfan", "monocrotophos", "phosphamidon", "methyl_parathion"
    ])

    @field_validator("banned_pesticides", mode="before")
    @classmethod
    def parse_banned_pesticides(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            cleaned = value.strip().strip("[]")
            if not cleaned:
                return []
            return [item.strip().strip('"\'') for item in cleaned.split(",") if item.strip()]
        if isinstance(value, list):
            return [str(item).strip().strip('"\'') for item in value if str(item).strip()]
        return value
    
    # UI
    default_language: Literal["en", "ur", "roman_ur"] = "en"
    enable_urdu_rendering: bool = True
    console_width: int = 100
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_file: str = "logs/kisan_dost.log"
    log_format: str = "json"

settings = Settings()