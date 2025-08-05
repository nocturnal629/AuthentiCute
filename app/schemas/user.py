from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserProfile(BaseModel):
    """Schema for user profile response"""
    id: int
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    """Schema for user profile update request"""
    name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None 