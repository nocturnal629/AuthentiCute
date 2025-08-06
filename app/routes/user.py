from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserProfile, UserProfileUpdate
from app.utils.db_utils import get_user_by_id, update_user
from app.utils.session_utils import get_user_from_session
from app.utils.rate_limiter import auth_rate_limiter
from app.utils.client_utils import get_rate_limit_identifier
from app.utils.error_handlers import handle_authentication_error, handle_validation_error, log_error

router = APIRouter(prefix="/api/users", tags=["User Management"])

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(session_token: str, request: Request, db: Session = Depends(get_db)):
    identifier = get_rate_limit_identifier(request)
    is_allowed, remaining = auth_rate_limiter.is_allowed(identifier)
    
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    try:
        user = get_user_from_session(db, session_token)
        if not user:
            raise handle_authentication_error("Invalid session")
        
        return UserProfile(
            id=user.id,
            email=user.email,
            name=user.name,
            phone=user.phone,
            bio=user.bio,
            oauth_provider=user.oauth_provider,
            oauth_id=user.oauth_id,
            is_verified=user.is_verified,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"endpoint": "get_user_profile"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get profile. Please try again."
        )

@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    session_token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    identifier = get_rate_limit_identifier(request)
    is_allowed, remaining = auth_rate_limiter.is_allowed(identifier)
    
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    try:
        user = get_user_from_session(db, session_token)
        if not user:
            raise handle_authentication_error("Invalid session")
        
        update_data = {}
        if profile_data.name is not None:
            update_data["name"] = profile_data.name
        if profile_data.phone is not None:
            update_data["phone"] = profile_data.phone
        if profile_data.bio is not None:
            update_data["bio"] = profile_data.bio
        
        updated_user = update_user(db, user.id, **update_data)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserProfile(
            id=updated_user.id,
            email=updated_user.email,
            name=updated_user.name,
            phone=updated_user.phone,
            bio=updated_user.bio,
            oauth_provider=updated_user.oauth_provider,
            oauth_id=updated_user.oauth_id,
            is_verified=updated_user.is_verified,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"endpoint": "update_user_profile"})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile. Please try again."
        )

@router.get("/{user_id}", response_model=UserProfile)
async def get_user_by_id_endpoint(
    user_id: int,
    session_token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    identifier = get_rate_limit_identifier(request)
    is_allowed, remaining = auth_rate_limiter.is_allowed(identifier)
    
    if not is_allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
    
    try:
        user = get_user_from_session(db, session_token)
        if not user:
            raise handle_authentication_error("Invalid session")
        
        target_user = get_user_by_id(db, user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserProfile(
            id=target_user.id,
            email=target_user.email,
            name=target_user.name,
            phone=target_user.phone,
            bio=target_user.bio,
            oauth_provider=target_user.oauth_provider,
            oauth_id=target_user.oauth_id,
            is_verified=target_user.is_verified,
            is_active=target_user.is_active,
            created_at=target_user.created_at,
            updated_at=target_user.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, {"endpoint": "get_user_by_id", "target_user_id": user_id})
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information. Please try again."
        ) 