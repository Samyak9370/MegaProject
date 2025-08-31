from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

class AnalysisType(str, Enum):
    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"
    CONFIDENCE = "confidence"
    FLUENCY = "fluency"
    OVERALL = "overall"

class FeedbackBase(BaseModel):
    session_id: str
    analysis_type: AnalysisType
    score: float = Field(..., ge=0, le=10)
    feedback: str
    suggestions: List[str]

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class SessionBase(BaseModel):
    user_id: str
    title: str
    description: Optional[str] = None
    duration_seconds: int

class SessionCreate(SessionBase):
    pass

class Session(SessionBase):
    id: str
    created_at: datetime
    feedbacks: List[Feedback] = []
    
    class Config:
        from_attributes = True

class AnalysisResult(BaseModel):
    transcript: str
    analysis: dict
    feedback: List[Feedback]
