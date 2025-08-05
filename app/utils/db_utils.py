from sqlalchemy.orm import Session
from app.models import User
from typing import Optional

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email address"""
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def create_user(
    db: Session, 
    email: str, 
    hashed_password: str = None, 
    name: str = None,
    oauth_provider: str = None,
    oauth_id: str = None,
    oauth_email: str = None,
    is_verified: bool = False
) -> User:
    """Create a new user (supports both regular and OAuth users)"""
    user = User(
        email=email,
        hashed_password=hashed_password,
        name=name,
        oauth_provider=oauth_provider,
        oauth_id=oauth_id,
        oauth_email=oauth_email,
        is_verified=is_verified
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user(db: Session, user_id: int, **kwargs) -> Optional[User]:
    """Update user information"""
    user = get_user_by_id(db, user_id)
    if user:
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user"""
    user = get_user_by_id(db, user_id)
    if user:
        db.delete(user)
        db.commit()
        return True
    return False

def verify_user_email(db: Session, user_id: int) -> bool:
    """Mark user email as verified"""
    user = get_user_by_id(db, user_id)
    if user:
        user.is_verified = True
        db.commit()
        return True
    return False 