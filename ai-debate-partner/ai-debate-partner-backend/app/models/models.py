from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum

class AnalysisType(str, enum.Enum):
    GRAMMAR = "grammar"
    VOCABULARY = "vocabulary"
    CONFIDENCE = "confidence"
    FLUENCY = "fluency"
    OVERALL = "overall"

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True)
    title = Column(String, index=True)
    description = Column(Text, nullable=True)
    duration_seconds = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    feedbacks = relationship("Feedback", back_populates="session")

class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    analysis_type = Column(Enum(AnalysisType))
    score = Column(Float)
    feedback = Column(Text)
    suggestions = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("Session", back_populates="feedbacks")
