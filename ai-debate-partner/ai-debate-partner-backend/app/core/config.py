from typing import List

class Settings:
    # App settings
    PROJECT_NAME: str = "AI Debate Partner API"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    ALGORITHM: str = "HS256"

    # OpenAI
    OPENAI_API_KEY: str = "your_openai_api_key_here"

    # Database
    DATABASE_URL: str = "sqlite:///./ai_debate.db"

    # CORS - Hardcoded for now to avoid parsing issues
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:5173"
    ]

    # Audio settings
    MAX_AUDIO_SIZE_MB: int = 50
    ALLOWED_AUDIO_TYPES: List[str] = ["audio/wav", "audio/mp3", "audio/mpeg"]
    AUDIO_UPLOAD_DIR: str = "./uploads/audio"

    # WebSocket
    WEBSOCKET_PATH: str = "/ws"

    # Logging
    LOG_LEVEL: str = "INFO"

# Create a single instance of the settings
settings = Settings()
