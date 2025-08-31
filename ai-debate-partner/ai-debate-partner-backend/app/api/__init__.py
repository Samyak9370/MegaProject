from fastapi import APIRouter
from .endpoints import speech, analysis, sessions, feedback

api_router = APIRouter()
api_router.include_router(speech.router, prefix="/speech", tags=["speech"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
