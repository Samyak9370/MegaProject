@echo off
echo Setting up AI Debate Partner Backend...

:: Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    echo # OpenAI API Key (required for text analysis)>> .env
    echo OPENAI_API_KEY=your_openai_api_key_here>> .env
    echo.>> .env
    echo # FastAPI Settings>> .env
    echo PROJECT_NAME="AI Debate Partner">> .env
    echo API_V1_STR=/api/v1>> .env
    echo SECRET_KEY=your-secret-key-here>> .env
    echo ACCESS_TOKEN_EXPIRE_MINUTES=1440>> .env
    echo.>> .env
    echo # Database Settings (SQLite by default)>> .env
    echo DATABASE_URL=sqlite:///./ai_debate.db>> .env
    echo.>> .env
    echo # CORS Settings (comma-separated string of allowed origins)>> .env
    echo BACKEND_CORS_ORIGINS="http://localhost:3000,http://localhost:8000,http://localhost:5173">> .env
    echo.>> .env
    echo # Audio Settings>> .env
    echo AUDIO_UPLOAD_DIR=./uploads/audio>> .env
    echo MAX_AUDIO_SIZE_MB=50>> .env
    echo.>> .env
    echo # WebSocket Settings>> .env
    echo WEBSOCKET_URL=ws://localhost:8000/ws/audio>> .env
    echo.>> .env
    echo # Logging Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)>> .env
    echo LOG_LEVEL=INFO>> .env
    echo.>> .env
    echo Please edit the .env file to add your OpenAI API key and other settings.>> .env
) else (
    echo .env file already exists, keeping existing configuration.
)

:: Create required directories
if not exist "uploads\audio" (
    mkdir uploads\audio
    echo Created uploads/audio directory
)

:: Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

:: Start the server
echo Starting FastAPI server...
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
