from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import UserSignup, UserLogin, UserResponse, SessionResponse, PasswordResetRequest, PasswordReset
from app.utils.auth_utils import hash_password, verify_password, send_verification_email, send_password_reset_email
from app.utils.db_utils import get_user_by_email, create_user, verify_user_email
from app.utils.session_utils import create_user_session, delete_session, get_user_from_session
from app.utils.token_utils import create_verification_token, get_verification_token, mark_verification_token_used, create_reset_token, get_reset_token, mark_reset_token_used

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/signup", response_model=dict)
async def signup(user_data: UserSignup, db: Session = Depends(get_db)):
    """Register a new user"""
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = hash_password(user_data.password)
    
    user = create_user(
        db=db,
        email=user_data.email,
        hashed_password=hashed_password,
        name=user_data.name
    )
    
    verification_token = create_verification_token(db, user.id)
    email_sent = send_verification_email(user_data.email, verification_token.token)
    
    if not email_sent:
        return {
            "message": "Account created successfully! Please check your email for verification.",
            "warning": "Email verification may be delayed. Please check your spam folder."
        }
    
    return {
        "message": "Account created successfully! Please check your email for verification."
    }

@router.post("/login", response_model=SessionResponse)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user and create session"""
    user = get_user_by_email(db, user_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    session = create_user_session(db, user.id)
    
    return SessionResponse(
        session_token=session.session_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            phone=user.phone,
            bio=user.bio,
            is_verified=user.is_verified,
            is_active=user.is_active,
            created_at=user.created_at
        ),
        expires_at=session.expires_at
    )

@router.post("/logout")
async def logout(session_token: str, db: Session = Depends(get_db)):
    """Logout user and delete session"""
    success = delete_session(db, session_token)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return {"message": "Logged out successfully"}

@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify user email with token"""
    verification_token = get_verification_token(db, token)
    if not verification_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    mark_verification_token_used(db, token)
    
    verify_user_email(db, verification_token.user_id)
    
    return {"message": "Email verified successfully!"}

@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """Send password reset email"""
    user = get_user_by_email(db, request.email)
    if not user:
        return {"message": "If the email exists, a password reset link has been sent."}
    
    reset_token = create_reset_token(db, user.id)
    
    email_sent = send_password_reset_email(request.email, reset_token.token)
    
    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reset email"
        )
    
    return {"message": "If the email exists, a password reset link has been sent."}

@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    """Reset password with token"""
    reset_token = get_reset_token(db, reset_data.token)
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    mark_reset_token_used(db, reset_data.token)
    
    hashed_password = hash_password(reset_data.new_password)
    
    from app.utils.db_utils import update_user
    update_user(db, reset_token.user_id, hashed_password=hashed_password)
    
    return {"message": "Password reset successfully!"}

@router.get("/me", response_model=UserResponse)
async def get_current_user(session_token: str, db: Session = Depends(get_db)):
    """Get current user from session"""
    user = get_user_from_session(db, session_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        phone=user.phone,
        bio=user.bio,
        is_verified=user.is_verified,
        is_active=user.is_active,
        created_at=user.created_at
    ) 