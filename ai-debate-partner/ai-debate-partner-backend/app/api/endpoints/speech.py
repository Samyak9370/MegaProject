from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import Optional
import uuid
from datetime import datetime

from ....core.config import settings
from ....models import schemas
from ....services import speech_service, analysis_service
from ....models.database import get_db

router = APIRouter()

@router.post("/analyze", response_model=schemas.AnalysisResult)
async def analyze_speech(
    audio_file: UploadFile = File(...),
    title: Optional[str] = "Debate Session",
    description: Optional[str] = None,
    db = Depends(get_db)
):
    """
    Analyze speech from an audio file and provide feedback.
    """
    # Validate file type
    if audio_file.content_type not in settings.ALLOWED_AUDIO_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not supported. Please upload one of: {', '.join(settings.ALLOWED_AUDIO_TYPES)}"
        )
    
    try:
        # Process audio file
        transcript, duration = await speech_service.process_audio(audio_file)
        
        # Analyze transcript
        analysis_result = await analysis_service.analyze_transcript(transcript)
        
        # Create session record
        session_id = str(uuid.uuid4())
        
        # In a real app, you would save this to a database
        # For now, we'll just return the analysis
        
        return {
            "transcript": transcript,
            "analysis": analysis_result["analysis"],
            "feedback": [
                {
                    "session_id": session_id,
                    "analysis_type": f["type"],
                    "score": f["score"],
                    "feedback": f["feedback"],
                    "suggestions": f["suggestions"]
                }
                for f in analysis_result["feedback"]
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing request: {str(e)}"
        )
