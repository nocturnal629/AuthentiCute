from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserProfile, UserProfileUpdate
from app.utils.db_utils import get_user_by_id, update_user
from app.utils.session_utils import get_user_from_session

router = APIRouter(prefix="/api/users", tags=["User Management"])

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(session_token: str, db: Session = Depends(get_db)):
    """Get current user's profile"""
    user = get_user_from_session(db, session_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
    return UserProfile(
        id=user.id,
        email=user.email,
        name=user.name,
        phone=user.phone,
        bio=user.bio,
        is_verified=user.is_verified,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )

@router.put("/profile", response_model=UserProfile)
async def update_user_profile(
    profile_data: UserProfileUpdate,
    session_token: str,
    db: Session = Depends(get_db)
):
    """Update current user's profile"""
    user = get_user_from_session(db, session_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
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
        is_verified=updated_user.is_verified,
        is_active=updated_user.is_active,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at
    )

@router.get("/{user_id}", response_model=UserProfile)
async def get_user_by_id_endpoint(
    user_id: int,
    session_token: str,
    db: Session = Depends(get_db)
):
    """Get user profile by ID (only for authenticated users)"""
    user = get_user_from_session(db, session_token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session"
        )
    
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
        is_verified=target_user.is_verified,
        is_active=target_user.is_active,
        created_at=target_user.created_at,
        updated_at=target_user.updated_at
    ) 