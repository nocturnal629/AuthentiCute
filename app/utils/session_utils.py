from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.session import UserSession
from app.models.user import User
from app.utils.auth_utils import generate_session_token

def create_user_session(db: Session, user_id: int, expires_in_hours: int = 24) -> UserSession:
    """Create a new user session"""
    session_token = generate_session_token()
    
    expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    session = UserSession(
        session_token=session_token,
        user_id=user_id,
        expires_at=expires_at
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session

def get_session_by_token(db: Session, session_token: str) -> Optional[UserSession]:
    """Get session by token if it's valid and not expired"""
    session = db.query(UserSession).filter(
        UserSession.session_token == session_token,
        UserSession.expires_at > datetime.utcnow()
    ).first()
    
    return session

def get_user_from_session(db: Session, session_token: str) -> Optional[User]:
    """Get user from session token"""
    session = get_session_by_token(db, session_token)
    if session:
        return session.user
    return None

def delete_session(db: Session, session_token: str) -> bool:
    """Delete a session by token"""
    session = db.query(UserSession).filter(UserSession.session_token == session_token).first()
    if session:
        db.delete(session)
        db.commit()
        return True
    return False

def delete_user_sessions(db: Session, user_id: int) -> int:
    """Delete all sessions for a user"""
    sessions = db.query(UserSession).filter(UserSession.user_id == user_id).all()
    count = len(sessions)
    for session in sessions:
        db.delete(session)
    db.commit()
    return count

def cleanup_expired_sessions(db: Session) -> int:
    """Clean up expired sessions"""
    expired_sessions = db.query(UserSession).filter(
        UserSession.expires_at <= datetime.utcnow()
    ).all()
    
    count = len(expired_sessions)
    for session in expired_sessions:
        db.delete(session)
    
    db.commit()
    return count 