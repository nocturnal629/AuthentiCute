from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import UserSignup, UserLogin, UserResponse, SessionResponse, PasswordResetRequest, PasswordReset
from app.utils.auth_utils import hash_password, verify_password, send_verification_email, send_password_reset_email
from app.utils.db_utils import get_user_by_email, create_user, verify_user_email
from app.utils.session_utils import create_user_session, delete_session, get_user_from_session
from app.utils.token_utils import create_verification_token, get_verification_token, mark_verification_token_used, create_reset_token, get_reset_token, mark_reset_token_used
from app.utils.oauth_utils import get_google_oauth_url, handle_google_callback
from app.utils.rate_limiter import auth_rate_limiter, signup_rate_limiter, password_reset_rate_limiter
from app.utils.client_utils import get_rate_limit_identifier
from app.utils.error_handlers import handle_authentication_error, handle_validation_error, handle_rate_limit_error, log_error

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/signup", response_model=dict)
async def signup(user_data: UserSignup, request: Request, db: Session = Depends(get_db)):
    identifier = get_rate_limit_identifier(request, user_data.email)
    is_allowed, remaining = signup_rate_limiter.is_allowed(identifier)
    
    if not is_allowed:
        raise handle_rate_limit_error()
    
    try:
        existing_user = get_user_by_email(db, user_data.email)
        if existing_user:
            raise handle_validation_error("Email already registered", "email")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"endpoint": "signup", "email": user_data.email})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create account. Please try again."
        )

@router.post("/login", response_model=SessionResponse)
async def login(user_data: UserLogin, request: Request, db: Session = Depends(get_db)):
    identifier = get_rate_limit_identifier(request, user_data.email)
    is_allowed, remaining = auth_rate_limiter.is_allowed(identifier)
    
    if not is_allowed:
        raise handle_rate_limit_error()
    
    try:
        user = get_user_by_email(db, user_data.email)
        if not user:
            raise handle_authentication_error("Invalid email or password")
        
        if not user.is_active:
            raise handle_authentication_error("Account is deactivated", "ACCOUNT_DEACTIVATED")
        
        if not verify_password(user_data.password, user.hashed_password):
            raise handle_authentication_error("Invalid email or password")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"endpoint": "login", "email": user_data.email})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )

@router.get("/google/login")
async def google_login():
    """Initiate Google OAuth login"""
    try:
        auth_url = get_google_oauth_url()
        return RedirectResponse(url=auth_url)
    except Exception as e:
        log_error(e, {"endpoint": "google_login"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate Google OAuth"
        )

@router.get("/google/callback")
async def google_callback(code: str, request: Request, db: Session = Depends(get_db)):
    try:
        user = handle_google_callback(db, code)
        if not user:
            raise handle_authentication_error("Failed to authenticate with Google")
        
        session = create_user_session(db, user.id)
        
        redirect_url = f"/dashboard?session_token={session.session_token}"
        return RedirectResponse(url=redirect_url)
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"endpoint": "google_callback", "code_length": len(code) if code else 0})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during Google OAuth. Please try again."
        )

@router.post("/logout")
async def logout(session_token: str, db: Session = Depends(get_db)):
    """Logout user and delete session"""
    try:
        success = delete_session(db, session_token)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return {"message": "Logged out successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"endpoint": "logout"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed. Please try again."
        )

@router.get("/verify-email")
async def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify user email with token"""
    try:
        verification_token = get_verification_token(db, token)
        if not verification_token:
            raise handle_validation_error("Invalid or expired verification token")
        
        mark_verification_token_used(db, token)
        verify_user_email(db, verification_token.user_id)
        
        return {"message": "Email verified successfully!"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"endpoint": "verify_email"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed. Please try again."
        )

@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest, req: Request, db: Session = Depends(get_db)):
    identifier = get_rate_limit_identifier(req, request.email)
    is_allowed, remaining = password_reset_rate_limiter.is_allowed(identifier)
    
    if not is_allowed:
        raise handle_rate_limit_error()
    
    try:
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
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"endpoint": "forgot_password", "email": request.email})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reset email. Please try again."
        )

@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset, db: Session = Depends(get_db)):
    """Reset password with token"""
    try:
        reset_token = get_reset_token(db, reset_data.token)
        if not reset_token:
            raise handle_validation_error("Invalid or expired reset token")
        
        mark_reset_token_used(db, reset_data.token)
        hashed_password = hash_password(reset_data.new_password)
        
        from app.utils.db_utils import update_user
        update_user(db, reset_token.user_id, hashed_password=hashed_password)
        
        return {"message": "Password reset successfully!"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"endpoint": "reset_password"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed. Please try again."
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(session_token: str, db: Session = Depends(get_db)):
    """Get current user from session"""
    try:
        user = get_user_from_session(db, session_token)
        if not user:
            raise handle_authentication_error("Invalid session")
        
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
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"endpoint": "get_current_user"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information. Please try again."
        ) 