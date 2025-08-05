from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from app.models.token import EmailVerificationToken, PasswordResetToken
from app.utils.auth_utils import generate_verification_token, generate_reset_token

def create_verification_token(db: Session, user_id: int, expires_in_hours: int = 24) -> EmailVerificationToken:
    """Create a new email verification token"""
    token = generate_verification_token()
    
    expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    verification_token = EmailVerificationToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at
    )
    
    db.add(verification_token)
    db.commit()
    db.refresh(verification_token)
    
    return verification_token

def get_verification_token(db: Session, token: str) -> Optional[EmailVerificationToken]:
    """Get verification token if it's valid and not expired"""
    verification_token = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == token,
        EmailVerificationToken.expires_at > datetime.utcnow(),
        EmailVerificationToken.used == False
    ).first()
    
    return verification_token

def mark_verification_token_used(db: Session, token: str) -> bool:
    """Mark a verification token as used"""
    verification_token = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == token
    ).first()
    
    if verification_token:
        verification_token.used = True
        db.commit()
        return True
    return False

def create_reset_token(db: Session, user_id: int, expires_in_hours: int = 1) -> PasswordResetToken:
    """Create a new password reset token"""
    token = generate_reset_token()
    
    expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    
    reset_token = PasswordResetToken(
        token=token,
        user_id=user_id,
        expires_at=expires_at
    )
    
    db.add(reset_token)
    db.commit()
    db.refresh(reset_token)
    
    return reset_token

def get_reset_token(db: Session, token: str) -> Optional[PasswordResetToken]:
    """Get reset token if it's valid and not expired"""
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.expires_at > datetime.utcnow(),
        PasswordResetToken.used == False
    ).first()
    
    return reset_token

def mark_reset_token_used(db: Session, token: str) -> bool:
    """Mark a reset token as used"""
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token
    ).first()
    
    if reset_token:
        reset_token.used = True
        db.commit()
        return True
    return False

def cleanup_expired_tokens(db: Session) -> int:
    """Clean up expired tokens"""
    expired_verification = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.expires_at <= datetime.utcnow()
    ).all()
    
    expired_reset = db.query(PasswordResetToken).filter(
        PasswordResetToken.expires_at <= datetime.utcnow()
    ).all()
    
    count = len(expired_verification) + len(expired_reset)
    
    for token in expired_verification:
        db.delete(token)
    
    for token in expired_reset:
        db.delete(token)
    
    db.commit()
    return count 