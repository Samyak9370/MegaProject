from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from ....models.models import Feedback as DBFeedback
from ....models.schemas import Feedback as FeedbackSchema, FeedbackCreate
from ....models.database import get_db

router = APIRouter(prefix="/feedback", tags=["feedback"])

@router.post("/", response_model=FeedbackSchema)
def create_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    """
    Create new feedback for a session
    """
    # Check if session exists
    session = db.query(DBSession).filter(DBSession.id == feedback.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    db_feedback = DBFeedback(
        session_id=feedback.session_id,
        analysis_type=feedback.analysis_type,
        score=feedback.score,
        feedback=feedback.feedback,
        suggestions=",".join(feedback.suggestions),
        created_at=datetime.utcnow()
    )
    
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

@router.get("/session/{session_id}", response_model=List[FeedbackSchema])
def get_feedback_for_session(session_id: str, db: Session = Depends(get_db)):
    """
    Get all feedback for a specific session
    """
    feedbacks = db.query(DBFeedback).filter(DBFeedback.session_id == session_id).all()
    if not feedbacks:
        raise HTTPException(status_code=404, detail="No feedback found for this session")
    return feedbacks

@router.get("/{feedback_id}", response_model=FeedbackSchema)
def get_feedback(feedback_id: int, db: Session = Depends(get_db)):
    """
    Get a specific feedback by ID
    """
    feedback = db.query(DBFeedback).filter(DBFeedback.id == feedback_id).first()
    if feedback is None:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback
