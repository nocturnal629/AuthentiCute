from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserSignup(BaseModel):
    """Schema for user signup request"""
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    """Schema for user login request"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    is_verified: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class SessionResponse(BaseModel):
    """Schema for session response"""
    session_token: str
    user: UserResponse
    expires_at: datetime
    
    class Config:
        from_attributes = True

class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr

class PasswordReset(BaseModel):
    """Schema for password reset"""
    token: str
    new_password: str 