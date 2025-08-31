import os

env_content = """# OpenAI API Key (required for text analysis)
OPENAI_API_KEY=your_openai_api_key_here

# FastAPI Settings
PROJECT_NAME=AI Debate Partner
API_V1_STR=/api/v1
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database Settings (SQLite by default)
DATABASE_URL=sqlite:///./ai_debate.db

# CORS Settings (comma-separated string of allowed origins)
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8000,http://localhost:5173

# Audio Settings
AUDIO_UPLOAD_DIR=./uploads/audio
MAX_AUDIO_SIZE_MB=50

# WebSocket Settings
WEBSOCKET_URL=ws://localhost:8000/ws/audio

# Logging Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO
"""

# Create the uploads/audio directory if it doesn't exist
os.makedirs("uploads/audio", exist_ok=True)

# Write the .env file
try:
    with open(".env", "w") as f:
        f.write(env_content)
    print("Successfully created .env file with default settings.")
    print("Please edit the .env file to add your OpenAI API key and other settings.")
except Exception as e:
    print(f"Error creating .env file: {e}")
