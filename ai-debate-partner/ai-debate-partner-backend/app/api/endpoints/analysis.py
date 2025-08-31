from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ....models import schemas, models
from ....models.database import get_db
from ....services import analysis_service

router = APIRouter()

@router.get("/sessions", response_model=List[schemas.Session])
async def get_sessions(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of analysis sessions with pagination.
    """
    sessions = db.query(models.Session).order_by(
        models.Session.created_at.desc()
    ).offset(skip).limit(limit).all()
    return sessions

@router.get("/sessions/{session_id}", response_model=schemas.Session)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific analysis session by ID.
    """
    session = db.query(models.Session).filter(
        models.Session.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return session

@router.get("/sessions/user/{user_id}", response_model=List[schemas.Session])
async def get_user_sessions(
    user_id: str,
    days: Optional[int] = 30,
    limit: Optional[int] = 10,
    db: Session = Depends(get_db)
):
    """
    Get sessions for a specific user, with optional date range filtering.
    """
    query = db.query(models.Session).filter(
        models.Session.user_id == user_id
    )
    
    if days:
        date_threshold = datetime.utcnow() - timedelta(days=days)
        query = query.filter(models.Session.created_at >= date_threshold)
    
    sessions = query.order_by(
        models.Session.created_at.desc()
    ).limit(limit).all()
    
    return sessions

@router.get("/sessions/{session_id}/feedback", response_model=List[schemas.Feedback])
async def get_session_feedback(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all feedback for a specific session.
    """
    feedback = db.query(models.Feedback).filter(
        models.Feedback.session_id == session_id
    ).all()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No feedback found for this session"
        )
    
    return feedback

@router.get("/analytics/user/{user_id}")
async def get_user_analytics(
    user_id: str,
    days: Optional[int] = 30,
    db: Session = Depends(get_db)
):
    """
    Get analytics for a specific user.
    """
    # Calculate date threshold
    date_threshold = datetime.utcnow() - timedelta(days=days)
    
    # Get all sessions for the user
    sessions = db.query(models.Session).filter(
        models.Session.user_id == user_id,
        models.Session.created_at >= date_threshold
    ).all()
    
    if not sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No sessions found for this user in the specified time period"
        )
    
    # Get all feedback for these sessions
    session_ids = [session.id for session in sessions]
    feedback_items = db.query(models.Feedback).filter(
        models.Feedback.session_id.in_(session_ids)
    ).all()
    
    # Calculate metrics
    total_sessions = len(sessions)
    total_duration = sum(session.duration_seconds for session in sessions)
    
    # Calculate average scores by category
    scores = {}
    for item in models.AnalysisType:
        category_feedback = [f for f in feedback_items if f.analysis_type == item.value]
        if category_feedback:
            scores[item.value] = sum(f.score for f in category_feedback) / len(category_feedback)
    
    # Calculate improvement over time (simple linear regression)
    improvement = {}
    for item in models.AnalysisType:
        category_scores = [
            (s.created_at, f.score)
            for s in sessions
            for f in s.feedbacks
            if f.analysis_type == item.value
        ]
        if len(category_scores) > 1:
            # Simple linear regression to calculate improvement trend
            x = [(dt - category_scores[0][0]).total_seconds() for dt, _ in category_scores]
            y = [score for _, score in category_scores]
            n = len(x)
            x_sum = sum(x)
            y_sum = sum(y)
            xy_sum = sum(xi * yi for xi, yi in zip(x, y))
            x_sq_sum = sum(xi ** 2 for xi in x)
            
            slope = (n * xy_sum - x_sum * y_sum) / (n * x_sq_sum - x_sum ** 2) if (n * x_sq_sum - x_sum ** 2) != 0 else 0
            improvement[item.value] = slope * 86400  # Convert to score change per day
    
    return {
        "total_sessions": total_sessions,
        "total_duration_seconds": total_duration,
        "average_scores": scores,
        "improvement_per_day": improvement,
        "time_period_days": days
    }
