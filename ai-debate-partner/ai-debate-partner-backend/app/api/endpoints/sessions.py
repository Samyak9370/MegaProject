from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from datetime import datetime

from ....models.models import Session as DBSession, Feedback as DBFeedback
from ....models.schemas import Session as SessionSchema, SessionCreate, Feedback as FeedbackSchema
from ....models.database import get_db

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("/", response_model=SessionSchema)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    """
    Create a new debate session
    """
    db_session = DBSession(
        id=str(uuid.uuid4()),
        user_id=session.user_id,
        title=session.title,
        description=session.description,
        duration_seconds=session.duration_seconds,
        created_at=datetime.utcnow()
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

@router.get("/{session_id}", response_model=SessionSchema)
def read_session(session_id: str, db: Session = Depends(get_db)):
    """
    Get a specific session by ID
    """
    db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if db_session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session

@router.get("/user/{user_id}", response_model=List[SessionSchema])
def read_user_sessions(user_id: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all sessions for a specific user
    """
    sessions = db.query(DBSession).filter(DBSession.user_id == user_id).offset(skip).limit(limit).all()
    return sessions
