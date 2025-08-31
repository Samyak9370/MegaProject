# AI Debate Partner - Backend

This is the backend service for the AI Debate Partner application, built with FastAPI. It provides APIs for analyzing speech, providing feedback, and tracking user progress.

## Features

- Real-time speech recognition
- AI-powered analysis of debate content
- Grammar and vocabulary checking
- Confidence and fluency analysis
- Session history and progress tracking
- RESTful API endpoints

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- ffmpeg (for audio processing)
- OpenAI API key

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/ai-debate-partner.git
   cd ai-debate-partner/ai-debate-partner-backend
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following content:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. Initialize the database:
   ```bash
   alembic upgrade head
   ```

## Running the Application

Start the FastAPI development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- Interactive API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

## Project Structure

```
ai-debate-partner-backend/
├── app/
│   ├── api/                 # API routes
│   ├── core/                # Core configuration
│   ├── models/              # Database models
│   ├── services/            # Business logic
│   └── main.py              # Application entry point
├── tests/                   # Test files
├── .env                     # Environment variables
├── .gitignore
├── alembic.ini              # Database migration configuration
├── requirements.txt         # Project dependencies
└── README.md
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | - |
| `DATABASE_URL` | Database connection URL | `sqlite:///./debate_analyzer.db` |
| `SECRET_KEY` | Secret key for JWT token generation | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token expiration time in minutes | `10080` (7 days) |

## API Endpoints

### Speech Analysis
- `POST /api/v1/speech/analyze` - Analyze speech from an audio file

### Analysis
- `GET /api/v1/analysis/sessions` - Get analysis sessions
- `GET /api/v1/analysis/sessions/{session_id}` - Get session details
- `GET /api/v1/analysis/sessions/user/{user_id}` - Get user sessions
- `GET /api/v1/analysis/sessions/{session_id}/feedback` - Get session feedback
- `GET /api/v1/analysis/analytics/user/{user_id}` - Get user analytics

## Development

### Running Tests
```bash
pytest
```

### Database Migrations
To create a new migration:
```bash
alembic revision --autogenerate -m "description of changes"
```

To apply migrations:
```bash
alembic upgrade head
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
