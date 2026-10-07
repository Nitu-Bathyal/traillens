import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_ENV: str = "development"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "https://traillens.onrender.com",
        "*"
    ]

    # AI Configuration
    # Options: "demo" (deterministic offline nature model), "open_model", "ollama", "huggingface"
    AI_PROVIDER: str = "demo"
    OPEN_MODEL_NAME: str = "google/gemma-2-2b-it"
    VISION_MODEL_NAME: str = "google/paligemma-3b-pt-224"
    OPEN_MODEL_LICENSE: str = "Gemma Terms of Use / Open Weights"
    HUGGINGFACE_API_KEY: str = ""
    HUGGINGFACE_INFERENCE_URL: str = "https://api-inference.huggingface.co/models"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Database: MongoDB Atlas (Optional - falls back to local SQLite/InMemory store)
    MONGODB_URI: str = ""
    MONGODB_DB_NAME: str = "traillens"

    # Narration: ElevenLabs (Optional - falls back to Web Speech synthesis)
    ELEVENLABS_API_KEY: str = ""
    ELEVENLABS_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"  # Clear, calming voice

    # Observability: Sentry (Optional)
    SENTRY_DSN: str = ""
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0

    # Image upload settings
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
